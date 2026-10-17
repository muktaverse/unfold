# Unfold

A calm mental wellness companion. Users record a daily mood check-in, see their week at a glance, get tips matched to how they feel, and can request a counselor when their recent mood stays low.

> Unfold is a self-care support tool, not a medical or diagnostic service. In an emergency call 112. Tele-MANAS: 14416.

## Features
- Register and log in (passwords stored as salted hashes)
- Daily mood check-in: score 1 to 5, optional tags, optional private note
- Dashboard with a 7-day mood trend chart and weekly statistics
- Tips matched to the latest mood
- Escalation: if the last 3 check-ins average 2.0 or lower, the user is offered a counselor referral
- Referral saved only after explicit consent
- Crisis helpline notice when a note contains distress keywords

## Screenshots
| Dashboard | Check-in |
| --- | --- |
| ![Dashboard] | ![Check-in] |

## Tech stack
Python 3, Flask, Oracle Database (Docker), python-oracledb, Jinja templates, Chart.js

## Run it locally
1. Clone the repository and open the folder:
```bash
   git clone https://github.com/muktaverse/unfold.git
   cd unfold
```
2. Create a virtual environment and install packages:
```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```
3. Copy `config.example.py` to `config.py` and fill in your Oracle username, password, connection string and a secret key.
4. In SQL Developer (or any Oracle client), run `schema.sql` to create the tables and starter data.
5. Start the app:
```bash
   python app.py
```
6. Open http://127.0.0.1:5001

## Demo data
Register an account with the email `demo@unfold.com`, then run `demo_reset.sql` to load one sample week.

## Project structure
```
app.py            routes and escalation logic
db.py             database connection (IST session time zone)
schema.sql        tables and seed data
demo_reset.sql    resets the demo account
templates/        HTML pages
static/           CSS and Chart.js
diagrams/         UML diagrams
config.example.py settings template (copy to config.py)
```

## Documentation
The SRS, UML diagrams and test cases are in the project report. UML diagrams are in the `diagrams/` folder.

## Limitations
Distress detection is simple keyword matching, journal notes are not encrypted, and counselors have no login in this version. Do not enter real personal information.