# Author: Prof. MM Ghassemi <ghassem3@msu.edu>

#--------------------------------------------------
# Import Requirements
#--------------------------------------------------
import os
import json
import requests
from tokenize import String
from flask import Flask
from flask_socketio import SocketIO
from flask_failsafe import failsafe

socketio = SocketIO()



#--------------------------------------------------
# Create a Failsafe Web Application
#--------------------------------------------------
@failsafe
def create_app(debug=False):
	app = Flask(__name__)

	# NEW IN HOMEWORK 3 ----------------------------
	# This will prevent issues with cached static files
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.debug = debug
	# The secret key is used to cryptographically-sign the cookies used for storing the session data.
	app.secret_key = 'AKWNF1231082fksejfOSEHFOISEHF24142124124124124iesfhsoijsopdjf'
	# ----------------------------------------------

	from .utils.database.database import database
	db = database()
	db.createTables(purge=False)
	
	# NEW IN HOMEWORK 3 ----------------------------
	# This will create a user
	db.createUser(email='owner@email.com' ,password='password', role='owner')
	db.createUser(email='guest@email.com' ,password='password', role='guest')
	# ----------------------------------------------
	#from packages.wordnik import WordApi, swagger
	#apiUrl = 'http://api.wordnik.com/v4'

	# querystring = {"letterPattern":"[a-zA-Z]{3,10}","limit":"1", "random":"true"}
	# headers = {
	# 	"X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
	# 	"X-RapidAPI-Key": "959c86c7a2msh639a0380e20c53ep167105jsn31c49aff3482"
	# }
	# while (True):
	# 	response = requests.request("GET", WORDS_API_URL, headers=headers, params=querystring)
	# 	word = json.loads(response.text)['word']
	# 	if (word.isalpha()):
	# 		print("valid word: ", word)
	# 		break
	# ----------------------------------------------

	socketio.init_app(app)

	with app.app_context():
		from . import routes
		return app
