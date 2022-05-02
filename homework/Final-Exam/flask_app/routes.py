# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from getpass import getuser
from operator import itemgetter
from wsgiref.util import request_uri
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from datetime import date, datetime
import requests
from . import socketio

db = database()
WORDS_API_URL = "https://wordsapiv1.p.rapidapi.com/words/"


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
	return db.reversibleEncrypt('decrypt', session['email']) if 'email' in session else 'Unknown'

@app.route('/login')
def login():
    if "email" in session:
        return redirect('/home')
    else:
	    return render_template('login.html', user=getUser())

@app.route('/signup')
def signup():
    if "email" in session:
        return redirect('/home')
    else:
	    return render_template('signup.html', user=getUser())

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/processlogin', methods = ["POST", "GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    exists = db.authenticate(form_fields['email'], form_fields['password'])
    if (exists['success'] == 1):
        session['email'] = db.reversibleEncrypt('encrypt', form_fields['email']) 
        session['wordleComplete'] = False
        return json.dumps({'success':1})
    else:
        return json.dumps({'success':0})

@app.route('/processSignup', methods = ["POST","GET"])
def processSignup():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    created = db.createUser(form_fields['email'], form_fields['password'], 'user')
    if (created['success'] == 1):
        session['email'] = db.reversibleEncrypt('encrypt', form_fields['email'])
        session['wordleComplete'] = False
        return json.dumps({'success':1})
    else:
        return json.dumps({'success':0})

#######################################################################################
# WORDLE RELATED    
#######################################################################################
def wordleCompare(correctWord, guessedWord):
    compareDict = {'success':1}
    for n in range(0, len(correctWord)):
        if (guessedWord[n] == correctWord[n]):
            compareDict[n] = "correct"
        elif (guessedWord[n] in correctWord):
            compareDict[n] = "present"
        else:
            compareDict[n] = "incorrect"

    return json.dumps(compareDict)


def wordInDictionary(word):
    headers = {
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
        "X-RapidAPI-Key": "959c86c7a2msh639a0380e20c53ep167105jsn31c49aff3482"
    }
    response = requests.request("GET", WORDS_API_URL + word, headers=headers)
    success = json.loads(response.text).get('success')
    if (success == False):
        return False

    return True

def createWord(date):
    querystring = {"letterPattern":"^[a-zA-Z]{1,10}$","limit":"1", "random":"true", "frequencymin":"6.0"}
    headers = {
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
        "X-RapidAPI-Key": "959c86c7a2msh639a0380e20c53ep167105jsn31c49aff3482"
    }
    while (True):
        response = requests.request("GET", WORDS_API_URL, headers=headers, params=querystring)
        word = json.loads(response.text)['word']
        if (word.isalpha()):
            db.addWord(word, date)
            return word

def getDailyWord():
    todays_date = str(datetime.today().date())
    daily_word = db.getWord(todays_date)
    if (daily_word['success'] == 0): # new day - fetch new word
        return createWord(todays_date)

    return daily_word['word']

@app.route('/wordle')
@login_required
def wordle():
    show_instructions = False
    if ('wordleVisited' not in session or session['wordleVisited'] == False): #first time user visits Wordle - show instructions
        show_instructions = True
        session['wordleVisited'] = True

    daily_word = getDailyWord()
    return render_template('wordle.html', user = getUser(), length = len(daily_word), instructions = show_instructions)

@app.route('/wordle/validateWord', methods = ["POST"])
def validateWord():
    fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    word = fields['word']

    if (not wordInDictionary(word)):
        return json.dumps({'success':0})

    return wordleCompare(getDailyWord(), word.lower())

@app.route('/wordle/addToLeaderboard', methods = ["POST"])
def addToLeaderboard():
    fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    email = getUser()
    todays_date = str(datetime.today().date())
    time = fields['seconds']
    completed = fields['completed']
    result = db.addToLeaderboard(email, todays_date, time, completed)
    if (result['success'] == 0):
        return json.dumps({'success':0})

    return json.dumps({'success':1})
    
@app.route('/wordle/leaderboard')
@login_required
def leaderboard():
    todays_date = str(datetime.today().date())
    scores = db.getLeaderBoardData(todays_date)
    scores_sorted = sorted(scores, key=itemgetter('time'))
    completed = str(db.onLeaderboard(getUser(), todays_date))
    return render_template('leaderboard.html', user = getUser(), scores_data = scores_sorted[0:5], date = todays_date, word = getDailyWord(), complete = completed)


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')


#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	return render_template('home.html', user=getUser())

@app.route('/projects')
def projects():
	return render_template('projects.html', user=getUser())

@app.route('/piano')
@login_required
def piano():
	return render_template('piano.html', user=getUser())

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	return render_template('resume.html', resume_data = resume_data, user=getUser())

@app.route('/processfeedback', methods= ['POST'])
def processfeedback():
	feedback = request.form
	db.insertRows('comments', ['name', 'email', 'comment'], [[feedback['name'], feedback['email'], feedback['feedback']]])
	return redirect('/feedback')

@app.route('/feedback')
def feedback():
	feedback_data = db.getFeedbackData()
	return render_template('feedback.html', feedback_data = feedback_data, user=getUser())

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
