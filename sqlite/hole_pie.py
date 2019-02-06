from . import Base
import logger

log = logger.get(__name__)


class HolePie(Base):

    def __init__(self):
        super().__init__()

    @property
    def table_name(self):
        return 'hole_pie'

    @property
    def no_pk_cols(self):
        return [
            'alias',
            'aim_host',
            'aim_port',
            'aim_user',
            'aim_pwd',
            'local_port',
            'proxy_host',
            'proxy_port',
            'proxy_user',
            'proxy_pwd',  # currently no-use
            'last_conn_time',
            'create_time',
            'update_time',
        ]

    def create_table(self, index=True):
        sql = '''
        create table {} (
            id INTEGER primary key AUTOINCREMENT, 
            alias varchar(20),
            aim_host varchar(50),
            aim_port varchar(8),
            aim_user varchar(20),
            aim_pwd varchar(20),
            local_port varchar(8),
            proxy_host varchar(50),
            proxy_port varchar(8),
            proxy_user varchar(20),
            proxy_pwd varchar(20),
            last_conn_time varchar(10),
            create_time varchar(10),
            update_time varchar(10)
        )
        '''.format(self.table_name)
        self.execute(sql)

        if index:
            self.create_index()

        self.commit()

    def create_index(self):
        sql = 'CREATE INDEX uniq_alias ON {} (alias)'\
            .format(self.table_name)
        self.execute(sql)

        # TODO idx_aim can be the unique key
        sql = 'CREATE INDEX idx_aim '\
        'ON {} (aim_host, aim_port, aim_user)'\
            .format(self.table_name)
        self.execute(sql)

    def insert_row(self, *params):
        sql = '''INSERT INTO {} (%s) VALUES (%s)''' % (
            self.no_pk_fields, 
            ', '.join(
                ['"{}"' for i in range(0, len(self.no_pk_cols))]
            )
        )
        sql = sql.format(self.table_name, *params)
        log.debug('sql: %s' % sql)
        _id = self.insert(sql)
        self.commit()
        return _id

    def delete_by_id(self, pkid):
        sql = '''
        DELETE FROM {} 
        WHERE id={}
        '''
        sql = sql.format(self.table_name, pkid)
        log.debug('sql: %s' % sql)
        self.delete(sql)
        self.commit()

    def get_by_aim(self, aim_host, aim_port, aim_user):
        sql = '''
        SELECT {}
        FROM {}
        WHERE aim_host=? AND aim_port=? AND aim_user=?
        ORDER BY id DESC
        LIMIT 1
        '''.format(self.full_fields, self.table_name)
        log.debug('sql: %s' % sql)
        rv = self.fetchone(sql, aim_host, aim_port, aim_user)
        return rv

    def get_by_alias(self, alias):
        sql = '''
        SELECT {}
        FROM {}
        WHERE alias=?
        ORDER BY id DESC
        LIMIT 1
        '''.format(self.full_fields, self.table_name)
        log.debug('sql: %s' % sql)
        rv = self.fetchone(sql, alias)
        return rv

    def list_all(self):
        sql = '''
        SELECT {}
        FROM {}
        ORDER BY id 
        '''.format(self.full_fields, self.table_name)
        log.debug('sql: %s' % sql)
        rv = self.fetchall(sql)
        return rv


def test_create():
    HolePie().create_table()


def test_insert():
    import time
    now = int(time.time())
    row_id = HolePie().insert_row(
        'fruit', 'rds.xxxxx.com', '3306', 
        'root', '123456', '9388', 'bridge.xxxxx.com', '22', 
        'dev', '', now, now, now
    )


def test_get_alias():
    rv = HolePie().get_by_alias('fruit')
    log.debug(rv)


def test_get_aim():
    rv = HolePie().get_by_aim('rds.xxxxx.com', '3306', 'root')
    log.debug(rv)


def test_list_all():
    rv = HolePie().list_all()
    log.debug(rv)
