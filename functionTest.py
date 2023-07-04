import pymysql
import unittest
from model import database, initdatabase

'''
Test the function of system.

Upadate 2023-6-26

'''


CONFIG = {

    "host": '127.0.0.1:3306',
    "user": 'root',
    "pwd": '1111',
    'db': 'Library'
}

class SystemFunctionTest(unittest.TestCase):

    def setUp(self):
        initdatabase.init_database()

    def test_sign_up(self):
        # test case 1
        user_message = {
            'SID': '010',
            'PASSWORD': '1234',
            'SNAME': '王小明',
            'DEPARTMENT': '计算机学院',
            'MAJOR': '软件工程',
            'MAX': 3
        }
        self.assertTrue(database.signup(user_message))

        # test case 2
        user_message = {
            'SID': '001',         # exist
            'PASSWORD': '000000',
            'SNAME': 'Amy',
            'DEPARTMENT': 'Mathematics',
            'MAJOR': 'Math',
            'MAX': 3
        }
        self.assertFalse(database.signup(user_message))
    

    def test_sign_in(self):
        # test case 1 -- student
        user_message = {
            'ID': '001',
            'PASSWORD': 'secret789'
        }
        info = database.signin(user_message)
        self.assertCountEqual(info['SNAME'], 'Tom Williams')

        # test case 2 -- admin
        user_message = {
            'ID': 'admin',
            'PASSWORD': '123456'
        }
        info = database.signin(user_message)
        self.assertEqual(info['class'], 'admin')

        # test case 3 -- not exist
        user_message = {
            'ID': '009',
            'PASSWORD': 'secret789'
        }
        info = database.signin(user_message)
        self.assertEqual(info, None)

        # test case 4 -- password error
        user_message = {
            'ID': '001',
            'PASSWORD': '0000'
        }
        info = database.signin(user_message)
        self.assertEqual(info, None)


    def test_update_student(self):
        user_message = {
            'SID': '001',
            'PASSWORD': 'secret789',
            'SNAME': 'Tom Williams',
            'DEPARTMENT': 'Computer',
            'MAJOR': 'Computer Science',
            'MAX': 5
        }
        self.assertTrue(database.update_student(user_message))



    def test_get_student_info(self):
        info = database.get_student_info('002')
        self.assertEqual(info['SNAME'], 'Jane Smith')
        self.assertEqual(info['DEPARTMENT'], 'Mathematics')
        self.assertEqual(info['MAJOR'], 'Applied Mathematics')
        self.assertEqual(info['MAX'], 3)
        info = database.get_student_info('102')


    def test_get_book_info(self):
        # test case 1
        info = database.get_book_info('B002')
        book_info = {
            'BID': 'B001',
            'BNAME': '活着',
            'AUTHOR': '余华',
            'PUBLICATION_DATE': '1993年',
            'PRESS': '作家出版社',
            'POSITION': 'A1',
            'SUM': 8,
            'NUM': 5,
            'CLASSIFICATION': str
        }
        self.assertCountEqual(info, book_info)
        info = database.get_book_info('B111')

    
    def test_borrow_return(self):
        # test case 1
        self.assertTrue(database.borrow_book('B010','001'))
        self.assertTrue(database.return_book('B010','001'))

        # test case 2
        self.assertFalse(database.return_book('B011','001'))

        # test case 3
        self.assertTrue(database.borrow_book('B012','001'))
        self.assertFalse(database.borrow_book('B012','001'))



    def test_delete_book(self):
        # test case 1
        self.assertTrue(database.delete_book('B015'))
        self.assertEqual(database.get_book_info('B015'), None)

        # test case 2 -- not exist
        self.assertTrue(database.delete_book('B016'))



    def test_add_book(self):
        # test case 1
        book_msg = {
            'BID': 'B016',
            'BNAME': '巴黎圣母院',
            'AUTHOR': '雨果',
            'PUBLICATION_DATE': '1831年',
            'PRESS': '法国出版社',
            'POSITION': 'W15',
            'SUM': 6,
            'CLASSIFICATION': '小说'
        }
        self.assertTrue(database.new_book(book_msg))

        # test case 2
        book_msg = {
            'BID': 'B001',    # exist
            'BNAME': 'xxxx',
            'AUTHOR': 'xx',
            'PUBLICATION_DATE': '1831年',
            'PRESS': '法国出版社',
            'POSITION': 'W15',
            'SUM': 6,
            'CLASSIFICATION': '小说'
        }
        self.assertFalse(database.new_book(book_msg))

        
    def test_get_log(self):
        database.get_log('001', True)


    def test_delete_book(self):
        # case 1
        self.assertTrue(database.delete_book('B001'))


    def test_delete_student(self):
        # case 1
        self.assertTrue(database.delete_student('001'))

if __name__ == '__main__':
    unittest.main()