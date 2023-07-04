import pymysql
from model import initdatabase
import unittest


CONFIG = {
    "host": 'localhost',
    "user": 'root',
    "pwd": '1111',
    'db': 'Library'
}

CASE1 = {
    "host": 'localhost',
    "user": 'root',
    "pwd": '12345',         # password error
    'db': 'Library'
}


class DatabaseTest(unittest.TestCase):

    @staticmethod
    def connection():
        # Test connection
        conn = pymysql.connect(
                    host = CONFIG['host'], 
                    user = CONFIG['user'], 
                    password = CONFIG['pwd']
                )
        cursor = conn.cursor()
        return conn, cursor
    


    def test_connection(self):
        conn, cursor = DatabaseTest.connection()
        print('Test connection PASS.')

    def test_error_connection(self):
        try:
            # Test connection error
            conn = pymysql.connect(
                        host = CASE1['host'], 
                        user = CASE1['user'], 
                        password = CASE1['pwd']
                    )
            cursor = conn.cursor()
        except Exception as e:
            print('Password Error.')
            print(e)


    def test_execute(self):
        conn, cursor = DatabaseTest.connection()
        # Test execute
        cursor.execute('DROP DATABASE IF EXISTS Library;')
        cursor.execute('CREATE DATABASE Library CHARACTER SET utf8;')
        cursor.execute('USE Library;')
        print('Test execute PASS.')


    def test_init_database(self):
        # Test init library
        initdatabase.init_database()
        print('Test init library PASS.')

    def test_primary(self):
        initdatabase.init_database()
        conn, cursor = DatabaseTest.connection()
        try:
            cursor.execute('USE Library;')
            cursor.execute(
            "INSERT INTO student (SID, PASSWORD, SNAME, DEPARTMENT, MAJOR, MAX) "\
            "VALUES  ('001', 'secret789', 'Tom Williams', 'Physics', 'Astrophysics', 5);"\
            )
        except Exception as e:
            print(e)   


if __name__ == '__main__':
    unittest.main()
