# -*- coding: utf-8 -*-

import os
import sqlite3


DIR_PATH = os.path.abspath(os.path.dirname(__file__))
# morry.db named for becoming the ssh larry of MySQL
DB_NAME = 'morry.db'
DB_LOCATION = os.path.abspath(os.path.join(DIR_PATH, '../' + DB_NAME))


class Base(object):

    def __init__(self):
        self._conn = None
        self._cursor = None

    @property
    def no_pk_cols(self):
        return []

    @property
    def no_pk_cols(self):
        return []

    @property
    def col_num(self):
        return len(self.no_pk_cols) + 1

    @property
    def no_pk_fields(self):
        return ', '.join(self.no_pk_cols)

    @property
    def full_fields(self):
        return 'id, ' + self.no_pk_fields

    @property
    def conn(self):
        if self._conn:
            return self._conn
        try:
            print('new conn')
            self._conn = sqlite3.connect(DB_LOCATION)
            return self._conn
        except sqlite3.Error as e:
            print(e)
            self._conn.close()

    @property
    def cursor(self):
        if self._cursor:
            return self._cursor
        try:
            print('new cursor')
            self._cursor = self.conn.cursor()
            return self._cursor
        except sqlite3.Error as e:
            print(e)
            self._cursor.close()
            self.conn.close()

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
        except sqlite3.Error as e:
            print(e)

    def commit(self):
        try:
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            self.conn.close()

    def disconn(self):
        self.cursor.close()
        self.conn.close()

    def fetchone(self, sql, *args):
        try:
            params = tuple(args)
            self.cursor.execute(sql, params)
            rv = self.cursor.fetchone()
        except sqlite3.Error as e:
            print(e)
        finally:
            self.disconn()
        return rv

    def fetchall(self, sql, *args):
        try:
            params = tuple(args)
            self.cursor.execute(sql, params)
            rv = self.cursor.fetchall()
        except sqlite3.Error as e:
            print(e)
        finally:
            self.disconn()
        return rv

    def insert(self, sql):
        _id = 0
        try:
            self.cursor.execute(sql)
            if self.cursor.rowcount > 0:
                _id = self.cursor.lastrowid
        except sqlite3.Error as e:
            app.logger.error(e)
        finally:
            self.cursor.close()
        return _id

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
        except sqlite3.Error as e:
            app.logger.error(e)
        finally:
            self.cursor.close()
