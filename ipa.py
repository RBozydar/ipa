#!/usr/bin/env python

import ipa_db
import ipa_config
import station
import train
import sys
import datetime

def timestamp():
    return datetime.datetime.now().ctime()

def create_db(db, _):
    """creates new DB"""
    db.remove()
    db.create()

def print_trains(db, _):
    """prints all trains from DB"""
    for train in db.get_trains():
        print train['train_name'].encode('utf-8')

def get_trains_from_stations():
    trains = {}

    for station_id, station_name in ipa_config.stations:
        arrivals = []
        try:
            arrivals, _ = station.get_station(station_id)
            print timestamp(), 'Visitied station', station_name.encode('utf-8')
        except:
            print timestamp(), 'Cannot get trains from station', station_name.encode('utf-8')

        for train in arrivals:
            trains[train['id']] = train

    return trains

def update_train(db, train):
    try:
        db.update_train(train['id'], train['number'], train['name'], train['operator'], train['date'], train['relation'])
        print timestamp(), 'Updated train', train['id'], train['name'].encode('utf-8')
    except Exception as e:
        print timestamp(), 'Failed to update train', train['id'], train['name'].encode('utf-8'), ':', e.message

def update_train_schedule(db, train_id):
    try:
        schedule = [(stop['stop_name'], stop['sched_arrive_time'], stop['arrive_delay'], stop['sched_dep_time'], stop['dep_delay'])
                        for stop in train.get_train(train_id)]
        if schedule != []:
            db.update_schedule(train_id, schedule)
            print timestamp(), 'Updated train schedule', train_id
        else:
            db.mark_as_inactive(train_id)
            print timestamp(), 'Mark as inactive train ', train_id
    except Exception as e:
        print timestamp(), 'Failed to update train schedule', train_id, ':', e.message

def update_trains(db, _):
    """updated trains in DB based on preconfigured set of stations"""

    trains = get_trains_from_stations()
    for train_id in trains:
        update_train(db, trains[train_id])

    for train in db.get_active_trains():
        update_train_schedule(db, train['train_id'])

def print_train(db, args):
    """prints train all-time schedule"""
    for schedule in db.get_train_schedules(args[0].decode('utf-8')):
        print schedule.values()
        print '-----------------------'
        for schedule_info in db.get_schedule_info(schedule['train_id']):
            print schedule_info.values()
        print

if __name__ == "__main__":
    commands = [create_db, print_trains, update_trains, print_train]
    command = None

    if len(sys.argv) > 1:
        for c in commands:
            if c.__name__ == sys.argv[1]:
                command = c
                break

    if command:
        db = ipa_db.Db(ipa_config.db_name)
        command(db, sys.argv[2:])
    else:
        print 'Commands:'
        for c in commands:
            print '\t', c.__name__, '--', c.__doc__
