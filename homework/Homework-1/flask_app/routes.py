# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template
from flask import redirect

@app.route('/<page>')
def route(page):
	return render_template(page)

@app.route("/")
def starting_url():
	return redirect("/home.html")