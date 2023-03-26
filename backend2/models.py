import json 

class Event(dict):
    def __init__(self, id, name, from_time, to_time, location, tags):
        dict.__init__(self, id=id, name=name, from_time=from_time, to_time=to_time, location=location, tags=tags)

class Journal(dict):
    def __init__(self, journal_id, user_id, title, journal, sentiment, posted_time, latitude, longitude):
        dict.__init__(self, journal_id=journal_id, user_id=user_id, title=title, journal=journal, sentiment=sentiment, posted_time=posted_time, latitude=latitude, longitude=longitude)

class User(dict):
    def __init__(self, id, name):
        dict.__init__(self, id=id, name=name)