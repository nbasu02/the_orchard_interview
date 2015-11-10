neilbasu_theorchard README
==================

1. First steps

First set up a virtual environment using virtualenv.  If you do not have it installed, you can do so
from a Linux terminal with:

- sudo easy_install virtualenv

Then:

- virtualenv [insert_directory_name_here]
- cd /path/to/your/venv/

Update your path to check the venv first for convenience
- source bin/activate

If you do not have postgresql installed, please do so.

2. Setting up this project

- cd <directory containing this file>

Now install this project into your virtual environment
- pip install -e .

Now install all additional libraries needed for this application
- pip install -r requirements.txt

Set up database.  You will be prompted for your postgresql user's username and password
- initialize_neilbasu_theorchard_db development.ini

Note: Please put the csv with restaurant data into neilbasu_theorchard/scripts/.  It cannot
be uploaded to github due to filesize restraints.
Next we load the restaurant data into our database.  This can easily take 2 hours
- python neilbasu_theorchard/scripts/parse_data.py

3. Running project
We have all of the pieces in place, now we just start the server...
- pserve development.ini

...and in our brower go to localhost:6543
You should see ten highly rated thai restaurants mapped out on google maps, with information listed below.
And sorry ahead of time, my HTML/CSS skills aren't amazing.
