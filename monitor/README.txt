monitor README
==================

System Dependencies:
--------------------
- mysql
- python
- virtualenv


Getting Started
---------------
- cd <directory containing this file>

- make a virtualenvironment and activate it:
  $ virtualenv env
  $ env/bin/activate

- install dependenicies:
  $ pip install -r requirements.txt 

- install this app into the environment 
  $ pip install -e .

- create a mysql database and user, grant permissions, and update
  development.ini to include the db connection url

- initialize the database (won't work if you haven't done the above!):
  - $VENV/bin/initialize_monitor_db development.ini

- start the app:
  $VENV/bin/pserve development.ini

