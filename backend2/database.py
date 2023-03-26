import logging
import os
import random
from sqlite3 import connect
import time
import uuid
import json
from datetime import datetime, timezone, timedelta
from json import JSONEncoder
from argparse import ArgumentParser, RawTextHelpFormatter
from models import Event, Journal, User
from distilroberta import analyze_sentiment

import psycopg2
from psycopg2.errors import SerializationFailure
import psycopg2.extras

from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, World!"

# Create event table in database
# Need to add app.route() for POST
def create_events():
    # psycopg2.extras.register_uuid()
    # ids = []
    # id1 = uuid.uuid4()
    # id2 = uuid.uuid4()
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS Event (id INT PRIMARY KEY, name STRING, from_time TIMESTAMP, to_time TIMESTAMP, location STRING, tags STRING)"
        )
        logging.debug("create_events(): status message: %s",
                      cur.statusmessage)
    conn.commit()

# Update event table
# Need to add app.route() for POST
def create_events_from_JSON(file):
    file = open(file)
    dict = json.load(file)
    with conn.cursor() as cur:
        for event in dict:
            cur.execute(f"""UPSERT INTO Event (id, name, from_time, to_time, location, tags) VALUES \
                ({event['event_id']}, '{event['event_name']}', '{event['event_from_time']}', '{event['event_to_time']}', '{event['event_location']}', '{event['event_tags']}')""")
    conn.commit()

### FIX!!!
@app.route("/api/events/", methods=['GET'])
def get_events():
    with conn.cursor() as cur:
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(1)
        cur.execute(f"""SELECT * FROM Event WHERE CAST(from_time as DATE)={f"'{today}'"} or CAST(from_time as DATE)={f"'{tomorrow}'"}""")
        rows = cur.fetchall()
    conn.commit()
    events = []
    for row in rows:
        events.append(Event(row['id'], row['name'], str(row['from_time']), str(row['to_time']), row['location'], row['tags'].split(',')[0]))
    json_obj = json.dumps(events, indent=2)
    return json_obj        

@app.route("/api/journals")
def createJournalTable():
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS Journal (journal_id STRING PRIMARY KEY, user_id UUID NOT NULL REFERENCES "user" (id) ON DELETE CASCADE, \
                title STRING, journal STRING, sentiment STRING, posted_time TIMESTAMP, latitude STRING, longitude STRING)"""
            # "DROP TABLE Journal"
        )
        logging.debug("create_events(): status message: %s",cur.statusmessage)
    conn.commit()

@app.route("/api/journals/analyze_sentiment", methods=["POST"])
def setUserJournal():
    journal_id = request.json.get('journal_id')
    user_id = request.json.get('user_id')
    title = request.json.get('title').replace("'", "\'\'")
    journal = request.json.get('journal').replace("'", "\'\'")
    sentiment = analyze_sentiment(title + ' ' + journal)
    posted_time = datetime.now()
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    with conn.cursor() as cur:
        cur.execute(f"""UPSERT INTO Journal (journal_id, user_id, title, journal, sentiment, posted_time, latitude, longitude) VALUES ('{journal_id}', '{user_id}', '{title}', '{journal}', '{sentiment}', '{posted_time}', '{latitude}', '{longitude}')""")
        logging.debug("create_events(): status message: %s",cur.statusmessage)
    conn.commit()

@app.route("/api/journals/all", methods=["GET"])
def getUserJournal():
    with conn.cursor() as cur:
        cur.execute(f"""SELECT * FROM Journal WHERE (posted_time >= CURRENT_DATE - INTERVAL '24 HOURS')""")
        rows= cur.fetchall()
    conn.commit()
    journals = []
    for row in rows:
        journals.append(Journal(row['journal_id'], row['user_id'], row['title'], row['journal'], row['sentiment'], str(row['posted_time']), row['latitude'], row['longitude']))
    json_obj = json.dumps(journals, indent=2)
    file = open("test.json", "w")
    file.write(json_obj)
    return json_obj      

### FIX!!!
@app.route("/api/journals/<journal_id>", methods=["GET"])
def getJournalByID(journal_id):
    with conn.cursor() as cur:
        cur.execute(f"""SELECT * FROM Journal WHERE journal_id='{journal_id}'""")
        rows = cur.fetchall()
    conn.commit()
    journals = []
    for row in rows:
        journals.append(Journal(row['journal_id'], row['user_id'], row['title'], row['journal'], row['sentiment'], str(row['posted_time']), row['longitude'], row['latitude']))
    json_obj = json.dumps(journals, indent=2)
    file = open("test.json", "w")
    file.write(json_obj)
    return json_obj      

@app.route("/api/users/<user_id>", methods=["GET"])
def getUserName(user_id):
    with conn.cursor() as cur:
        cur.execute(f"""SELECT * FROM "user" WHERE id='{user_id}'""")
        rows = cur.fetchall()
    conn.commit()
    users = []
    for row in rows:
        users.append(User(str(row['id']), row['name']))
    json_obj = json.dumps(users, indent=2)
    return json_obj    

def parse_cmdline():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-v", "--verbose",
                        action="store_true", help="print debug info")

    parser.add_argument(
        "dsn",
        default=os.environ.get("DATABASE_URL"),
        nargs="?",
        help="""\
database connection string\
 (default: value of the DATABASE_URL environment variable)
            """,
    )

    opt = parser.parse_args()
    if opt.dsn is None:
        parser.error("database connection string not set")
    return opt


if __name__ == "__main__":
    opt = parse_cmdline()
    logging.basicConfig(level=logging.DEBUG if opt.verbose else logging.INFO)
    try:
        db_url = opt.dsn
        conn = psycopg2.connect(db_url,
                                cursor_factory=psycopg2.extras.RealDictCursor)
    except Exception as e:
        logging.fatal("database connection failed")
        logging.fatal(e)
    
    app.run()
