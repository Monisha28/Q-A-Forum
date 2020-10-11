# Q&A Forum
Question and Answer discussion platform app built using Flask

**To run the app locally follow the below steps..**

__Requirements__
flask
werkzeug
click

__Clone the repository__
$ git clone https://github.com/pallets/flask
$ cd flask

__Create a virtualenv and activate it__
$ python3 -m venv venv
$ . venv/bin/activate

__Run the app__
$ export FLASK_APP=task
$ export FLASK_ENV=development
$ flask init-db
$ flask run
