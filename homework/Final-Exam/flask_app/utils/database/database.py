from datetime import datetime
from inspect import Parameter
import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users', 'dailywords', 'leaderboard']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        user_row = self.query("SELECT 1 FROM `users` WHERE email=%s", parameters=[email])
        if (user_row): # user exists already
            return {'success': 0}

        self.insertRows('users', ['role', 'email', 'password'], [[role, email, self.onewayEncrypt(password)]])
        return {'success': 1}

    def authenticate(self, email='me@email.com', password='password'):
        user_row = self.query("SELECT 1 FROM `users` WHERE email=%s AND password=%s", parameters=[email, self.onewayEncrypt(password)])
        if (user_row):
            return {'success': 1}

        return {'success': 0}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message

#######################################################################################
# WORDLE RELATED
#######################################################################################
    def getWord(self, date):
        word_row = self.query("SELECT * FROM `dailywords` WHERE date=%s", parameters=[date])
        if (word_row):
            return {'success': 1, 'word': word_row[0]['word']}

        return {'success': 0}

    def addWord(self, word, date):
        status = self.getWord(date)
        if (status['success'] == 0): # no word on this day - safe to add
            self.insertRows('dailywords', ['word', 'date'], [[word, date]])
            return {'success': 1}

        return {'success': 0}

    def getLeaderBoardData(self, date):
        # get all scores on leaderboard from given date and return as array of dicts
        score_rows = self.query("SELECT `email`, `time`, `date` FROM `leaderboard` WHERE date=%s AND completed='true'", parameters=[date])
        return score_rows

    def onLeaderboard(self, email, date):
        score_row = self.query("SELECT * FROM `leaderboard` WHERE email=%s AND date=%s", parameters=[email, date])
        if (score_row):
            return True
        return False

    def addToLeaderboard(self, email, date, time, completed):
        onLeaderboard = self.onLeaderboard(email, date)
        if (onLeaderboard): # user already on leaderboard for current day - dont re-add
            return {'success': 0} 
        
        self.insertRows('leaderboard', ['email', 'time', 'date', 'completed'], [[email, time, date, completed]])
        return {'success': 1}


#######################################################################################
# PROJECT 2 RELATED
#######################################################################################
    """
    Formats the datetime object to the format: Month Name, Year 
    """
    def handleDate(self, date, end=False):
        if (end and date is None):
            return 'Present'

        elif (date is None):
            return ''

        else:
            return f'{date.strftime("%B")} {date.year}'



    def getResumeData(self):
        resume_data = {} 
        # iterate through each institution
        inst_rows = self.query("SELECT * FROM `institutions`")
        for inst in inst_rows:
            inst_id = inst['inst_id']
            resume_data[inst_id] = {
                'address' : inst['address'],
                'city' : inst['city'],
                'state' : inst['state'],
                'type' : inst['type'],
                'zip' : inst['zip'],
                'department' : inst['department'],
                'name' : inst['name'],
                'positions' : {},
            }
            # add each position that has this institutions id as a foreign key to the 'positions' dict
            pos_rows = self.query("SELECT * FROM `positions` WHERE inst_id=%s", parameters=[inst_id])
            for pos in pos_rows:
                pos_id = pos['position_id']
                resume_data[inst_id]['positions'][pos_id] = {
                    'end_date' : self.handleDate(pos['end_date'], True), 
                    'start_date' : self.handleDate(pos['start_date']),
                    'responsibilities' : pos['responsibilities'],
                    'title' : pos['title'],
                    'experiences' : {},
                }
                # add each experience that has this positions id as a foreign key to the 'experiences' dict
                exp_rows = self.query("SELECT * FROM `experiences` WHERE position_id=%s", parameters=[pos_id])
                for exp in exp_rows:
                    exp_id = exp['experience_id']
                    resume_data[inst_id]['positions'][pos_id]['experiences'][exp_id] = {
                        'name' : exp['name'],
                        'description' : exp['description'],
                        'end_date' : self.handleDate(exp['end_date'], True), 
                        'start_date' : self.handleDate(exp['start_date']),
                        'hyperlink' : exp['hyperlink'],
                        'skills' : {}
                    }
                    # add each skill that has this experiences id as a foreign key to the 'skills' dict
                    skill_rows = self.query("SELECT * FROM `skills` WHERE experience_id=%s", parameters=[exp_id])
                    for skill in skill_rows:
                        skill_id = skill['skill_id']
                        resume_data[inst_id]['positions'][pos_id]['experiences'][exp_id]['skills'][skill_id] = {
                            'name' : skill['name'],
                            'skill_level' : skill['skill_level']
                        }

        return resume_data

    def getFeedbackData(self):
        # get all feedback and return as array of dicts
        feedback_rows = self.query("SELECT `name`, `email`, `comment` FROM `comments`")
        return feedback_rows


