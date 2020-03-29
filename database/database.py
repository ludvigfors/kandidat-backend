import sqlalchemy as sql

FILE_NAME = "database/database.db"

class Database:
    __FILE_NAME = "database/database.db"

    def __init__(self):
        self.__engine = sql.create_engine('sqlite:///' + FILE_NAME, echo=False)
        self.__metadata = sql.MetaData(bind=self.__engine)
        self.__metadata.reflect()
        self.__verify_tables()
        
    def __verify_tables(self):
        if not self.has_table('sessions'):
            print("Session table missing, creating table")
            sql.Table('sessions', self.__metadata,
                sql.Column('id',            sql.Integer, primary_key=True),
                sql.Column('start_time',    sql.Integer, nullable=False),
                sql.Column('end_time',      sql.Integer, nullable=True),
                sql.Column('drone_mode',    sql.Integer, nullable=False))
        if not self.has_table('clients'):
            print('Clients table missing, creating table')
            sql.Table('clients', self.__metadata,
                sql.Column('id',                    sql.Integer, primary_key=True),
                sql.Column('session',               sql.Integer, sql.ForeignKey('sessions.id'), nullable=False),
                sql.Column('up_left_coordinate',    sql.Float),
                sql.Column('up_right_coordinate',   sql.Float),
                sql.Column('down_left_coordinate',  sql.Float),
                sql.Column('down_right_coordinate', sql.Float))
        if not self.has_table('areas'):
            print("Areas table missing, creating table")
            sql.Table('areas', self.__metadata,
                sql.Column('session',       sql.Integer, sql.ForeignKey('sessions.id'), primary_key=True),
                sql.Column('no',            sql.Float, primary_key=True),
                sql.Column('coordinate',    sql.Float, nullable=False))
        if not self.has_table('images'):
            print("Images table missing, creating table")
            sql.Table('images', self.__metadata,
                sql.Column('id', sql.Integer, primary_key=True),
                sql.Column('session', sql.Integer, sql.ForeignKey('sessions.id')),
                sql.Column('time_taken', sql.Integer, nullable=False),
                sql.Column('width', sql.Integer, nullable=False),
                sql.Column('height', sql.Integer, nullable=False),
                sql.Column('type', sql.String, nullable=False),
                sql.Column('up_left_coordinate',    sql.Float),
                sql.Column('up_right_coordinate',   sql.Float),
                sql.Column('down_left_coordinate',  sql.Float),
                sql.Column('down_right_coordinate', sql.Float),
                sql.Column('file_name', sql.String, nullable=False))
        if not self.has_table('prio_images'):
            print("prio_images table missing, creating table")
            sql.Table('prio_images', self.__metadata,
                sql.Column('id', sql.Integer, primary_key=True),
                sql.Column('session', sql.Integer, sql.ForeignKey('sessions.id'), nullable=False),
                sql.Column('time_requested', sql.Integer, sql.ForeignKey('sessions.id'), nullable=False),
                sql.Column('coordinate', sql.Float, nullable=False),
                sql.Column('status', sql.String, nullable=False),
                sql.Column('image', sql.Integer, sql.ForeignKey('sessions.id'), nullable=True),
                sql.Column('eta', sql.Integer, nullable=True))
        if not self.has_table('drones'):
            print("drones table missing, creating table")
            sql.Table('drones', self.__metadata,
                sql.Column('id', sql.Integer, primary_key=True),
                sql.Column('session', sql.Integer, sql.ForeignKey('sessions.id')),
                sql.Column('time_last_updated', sql.Integer),
                sql.Column('eta', sql.Integer))
        self.__metadata.create_all()

    def has_table(self, name):
        return name in self.__metadata.tables.keys()

    def get_table_names(self):
        return [table.name for table in self.__metadata.sorted_tables]

if __name__ == "__main__":
    database = Database()
    print(database.get_table_names())