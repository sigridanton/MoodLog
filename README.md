# About this app

*The* best app for reviewing your day! Add notes and emotions and see statistics about your mental health.

# For developers

Install pipenv and use it to install django into a separate directory. Then clone the code from GitHub or extract the zip file into the directory and run manage.py.

To run this app, the following dependancies must be installed with pip:
- `calendar`
- `matplotlib`
- `numpy`
- `django-multiselectfield`

To run this app:
  1. Set up the virtual environment and run `pipenv install django`
  2. Clone the repo from git using `git clone https://github.com/sigridanton/MoodLog` or download the zip file from releases and extract into the desired directory
  3. Run the app using `python manage.py runserver`