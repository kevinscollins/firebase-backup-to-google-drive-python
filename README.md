Backup Firebase data to Google Drive
==============================

Using python, you can automatically (with cron or heroku scheduler) backup all
your Firebase data and store it safely on Google Drive

The result is a new .json file in your S3 bucket whenever you run this script.

Install
-------

    virtualenv -p python2.7 --distribute venv
    source venv/bin/activate
    pip install -r requirements.txt


Run
---

Set your variables in config.py (copy from config-example.py), generate a Google Credential file and run:

    python backup-firebase.py
