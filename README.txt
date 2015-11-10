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

4. Schema

See schema.png for a diagram of the (very simple) schema.  For MVP, only three tables were made: CuisineType,
Restaurant, and Inspection.

CuisineType is simply what kind of restaurant it is (Thai, American, etc.) and only has one column besides id.

Restaurant has one cuisine type, and many inspections, each being some health inspection done of the establishment.
Though the inspections are given letter grades, it made more sense to store them as integers, as sorting on the
column was desired.  An arbitrary 1-5 scale was assigned to the letter grades, with 5 being the highest.  These
grades automatically update Restaurant's grade (a float between 1-5) for easier queries.

The project, being small, has a lot it could expand on in the future that was not done here.  For example,
an inspection and a grade could become separate entities as different types of inspections are explored.
If user reviews of restaurants are added, the quality of a restaurant can be the combination of user and health
reviews.

5. Testing

Just run

- nosetests

:)
