import mysql.connector
import ipa_db_schema

class Db:
    def __init__(self, db_config):
        self.conn = mysql.connector.connect(**db_config)

    def __del__(self):
        self.conn.close()

    def _execute(self, sql, args = tuple()):
        c = self.conn.cursor()
        c.execute(sql, args)
        return c

    def _format_select(self, cursor):
        names = [desc[0] for desc in cursor.description]
        for row in cursor:
            yield dict(zip(names, row))

    def commit(self):
        self.conn.commit()

    def remove_schema(self):
        for table in ipa_db_schema.tables:
            self._execute(table.drop)

    def create_schema(self):
        for table in ipa_db_schema.tables:
            self._execute(table.create)

    def select_query(self, query, args = tuple()):
        return self._format_select(self._execute(query, args))

    def get_trains(self):
        return self.select_query('SELECT * FROM train ORDER BY train_name')

    def get_active_schedules(self):
        return self.select_query('SELECT * FROM schedule WHERE active = 1')

    def mark_as_inactive(self, schedule_id):
        self._execute('''UPDATE schedule SET active = 0 WHERE schedule_id = %s''', (schedule_id,))

    def add_train(self, train_name):
        self._execute('''INSERT INTO train VALUES('', %s)''', (train_name,))

    def get_train_id(self, train_name):
        return self.select_query('SELECT train_id FROM train WHERE train_name = %s', (train_name,))

    def add_station(self, station_name):
        self._execute('''INSERT INTO station VALUES('', %s)''', (station_name,))

    def get_station_id(self, station_name):
        return self.select_query('SELECT station_id FROM station WHERE station_name = %s', (station_name,))

    def update_schedule(self, schedule_id, schedule_date, train_id):
        self._execute('''REPLACE INTO schedule VALUES(%s, %s, %s, 1)''', (schedule_id, schedule_date, train_id))

    def get_schedules(self, train_id):
        return self.select_query('''SELECT * FROM schedule INNER JOIN train USING (train_id)
                                    WHERE schedule.train_id = %s ORDER BY schedule_date''', (train_id,))

    def update_schedule_info(self, schedule_id, stop_number, station_id, info):
        self._execute('''REPLACE INTO schedule_info VALUES
                         (%s, %s, %s, %s, %s, %s, %s)''',
                         (schedule_id, stop_number, station_id,
                          info['arrival_time'], info['arrival_delay'],
                          info['departure_time'], info['departure_delay']))

    def get_schedule_infos(self, schedule_id):
        return self.select_query('''SELECT * FROM schedule_info INNER JOIN station USING (station_id)
                                    WHERE schedule_id = %s ORDER BY stop_number''', (schedule_id,))
