from sqlite3 import Error

import sqlite3

class InvPendDatabase:

    def __init__(self, database_name):
        self.database_name = database_name
        self.conn = self.create_connection()

        self.create_table(
            '''CREATE TABLE imu_data(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time REAL,
            angle_x REAL,
            angle_y REAL,
            angle_z REAL
            );'''
        )

    def create_connection(self):
        """ create a table from the create_table_sql statement """
        try:
            return sqlite3.connect(self.database_name)
        except Error as e:
            print(e)

    def create_table(self, create_table_sql):
        """ create table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def add_imu_data(self, data):
        """
            Insert IMU data into imu_data table
        """
        sql = ''' INSERT INTO imu_data(time, angle_x, angle_y, angle_z)
                  VALUES(?, ?, ?, ?) '''
        cur = self.conn.cursor()
        cur.execute(sql, data)
        self.conn.commit()
        return cur.lastrowid
    
    def all_imu_data(self):
        """
        Returns all data for a given gyro axis
        """

        sql = ('''
               SELECT *
               FROM imu_data
               ''')
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()



    def get_column_data(self, table_name, column_name):
        """
        Get all values from a specific column in a table.

        :param db_path: Path to SQLite3 database file.
        :param table_name: Name of the table.
        :param column_name: Name of the column.
        :return: List containing data from the specified column.
        """
        # Connect to the database
        cur = self.conn.cursor()

        # Execute the SELECT query
        cur.execute(f"SELECT {column_name} FROM {table_name}")

        # Fetch all the results
        results = cur.fetchall()

        # Unpack results from tuples and return as a list
        return [item[0] for item in results]



