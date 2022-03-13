import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import datetime
import time
class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'

    def query(self, query = "SELECT CURDATE()", parameters = None):

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

    def about(self, nested=False):    
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment']     = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name']     = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name']      = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key']             = row['is_key']
            table_info[row['table']][row['column_name']]['table']              = row['table']
        return table_info


    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        # Delete any existing tables to Re-Init the data (feedback is persistant so it must not be deleted)
        self.query(f'DROP TABLE IF EXISTS `skills`;')
        self.query(f'DROP TABLE IF EXISTS `experiences`;')
        self.query(f'DROP TABLE IF EXISTS `positions`;')
        self.query(f'DROP TABLE IF EXISTS `institutions`;')

        if (purge == True):
            self.query(f'DROP TABLE IF EXISTS `comments`;')

        table_path = data_path + 'create_tables/'
        initial_data_path = data_path + 'initial_data/'

        # initialize institutions table
        table_stream = open(table_path + 'institutions.sql')
        institution_def = table_stream.read()
        self.query(institution_def)

        initial_stream = open(initial_data_path + 'institutions.csv')
        initial_reader = csv.reader(initial_stream)

        institutions_cols = next(initial_reader)
        institutions_params = []
        for row in initial_reader:
            institutions_params.append(row)

        self.insertRows('institutions', institutions_cols, institutions_params)
        table_stream.close()
        initial_stream.close()

        # initialize positons table
        table_stream = open(table_path + 'positions.sql')
        position_def = table_stream.read()
        self.query(position_def)

        initial_stream = open(initial_data_path + 'positions.csv')
        initial_reader = csv.reader(initial_stream)

        positions_cols = next(initial_reader)
        positions_params = []
        for row in initial_reader:
            positions_params.append(row)

        self.insertRows('positions', positions_cols, positions_params)
        table_stream.close()
        initial_stream.close()

        # initialize experiences table
        table_stream = open(table_path + 'experiences.sql')
        experience_def = table_stream.read()
        self.query(experience_def)

        initial_stream = open(initial_data_path + 'experiences.csv')
        initial_reader = csv.reader(initial_stream)

        experiences_cols = next(initial_reader)
        experiences_params = []
        for row in initial_reader:
            experiences_params.append(row)

        self.insertRows('experiences', experiences_cols, experiences_params)
        table_stream.close()
        initial_stream.close()

        # initialize skills table
        table_stream = open(table_path + 'skills.sql')
        skill_def = table_stream.read()
        self.query(skill_def)

        initial_stream = open(initial_data_path + 'skills.csv')
        initial_reader = csv.reader(initial_stream)

        skills_cols = next(initial_reader)
        skills_params = []
        for row in initial_reader:
            skills_params.append(row)

        self.insertRows('skills', skills_cols, skills_params)
        table_stream.close()
        initial_stream.close()

        # initialize feedback table
        table_stream = open(table_path + 'feedback.sql')
        feedback_def = table_stream.read()
        self.query(feedback_def)
        table_stream.close()


    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        col_str = ','.join([f'`{field}`' for field in columns])
        query = f'INSERT INTO `{table}` (' + col_str + ') VALUES ('

        for param_list in parameters:
            param_str = ','.join([f'{param}' if param.isdigit() or param == "NULL" else f'\'{param}\'' for param in param_list])
            self.query(query + param_str + ');')


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