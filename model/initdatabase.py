import pymysql


CONFIG = {
    "host": 'localhost',
    "user": 'root',
    "pwd": '111',
    'db': 'Library'
}

# 数据库初始化
def init_database():
    try:
        conn = None
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('DROP DATABASE IF EXISTS Library;')
        cursor.execute('CREATE DATABASE Library CHARACTER SET utf8;')
        cursor.execute('USE Library;')
        cursor.execute(
        'CREATE TABLE student(' \
            'SID char(15) PRIMARY KEY,' \
            'PASSWORD char(20) NOT NULL,' \
            'SNAME varchar(20) NOT NULL,'\
            'DEPARTMENT varchar(40),'\
            'MAJOR varchar(20),'\
            'MAX int);'
        )
        
        cursor.execute(
        'CREATE TABLE administrator('\
            'AID char(15) PRIMARY KEY,'\
            'PASSWORD char(70));'
        )
        cursor.execute(
        'CREATE TABLE book('\
            'BID char(15) PRIMARY KEY,'\
            'BNAME varchar(40),'\
            'AUTHOR varchar(20),'\
            'PUBLICATION_DATE varchar(40),'\
            'PRESS varchar(20),'\
            'POSITION char(10),'\
            'SUM int,'\
            'NUM int);'
        )

        cursor.execute(
        'CREATE TABLE borrowing_book('\
            'BID char(15),'\
            'SID char(15),'\
            'BORROW_DATE char(17),'\
            'DEADLINE char(17),'\
            'PUNISH int,'\
            'PRIMARY KEY(BID, SID));'
        )

        cursor.execute(
        'CREATE TABLE log('\
            'BID char(15),'\
            'SID char(15),'\
            'BORROW_DATE char(17),'\
            'BACK_DATE char(17),'\
            'PUNISHED int);'
        )

        cursor.execute(
        'CREATE TABLE classification('\
            'BID char(15),'\
            'CLASSIFICATION nchar(15),'\
            'PRIMARY KEY(BID, CLASSIFICATION));'
        )

        cursor.execute("INSERT IGNORE INTO administrator VALUES('admin', '123456');")

        cursor.execute(
        "INSERT INTO book (BID, BNAME, AUTHOR, PUBLICATION_DATE, PRESS, POSITION, SUM, NUM) "\
        "VALUES  ('B001', '活着', '余华', '1993年', '作家出版社', 'A1', 8, 5),"\
                "('B002', '解忧杂货店', '东野圭吾', '2012年', '南海出版公司', 'A2', 7, 4),"\
                "('B003', '围城', '钱钟书', '1947年', '上海文艺出版社', 'A3', 9, 6),"\
                "('B004', '平凡的世界', '路遥', '1986年', '人民文学出版社', 'A4', 6, 3),"\
                "('B005', '三体', '刘慈欣', '2006年', '重庆出版社', 'A5', 10, 7),"\
                "('B006', '红楼梦', '曹雪芹', '18世纪', '人民文学出版社', 'A6', 9, 4),"\
                "('B007', '百年孤独', '加西亚·马尔克斯', '1967年', '上海译文出版社', 'A7', 10, 6),"\
                "('B008', '活着就是为了讲述', '刘震云', '2011年', '北京联合出版公司', 'A8', 7, 5),"\
                "('B009', '追风筝的人', '卡勒德·胡赛尼', '2003年', '上海人民出版社', 'A9', 8, 3),"\
                "('B010', '白夜行', '东野圭吾', '1997年', '文艺出版社', 'A10', 9, 5),"\
                "('B011', '红与黑', '司汤达', '1830年', '商务印书馆', 'A12', 10, 8),"\
                "('B012', '白银时代', '王小波', '1997年', '北京十月文艺出版社', 'A13', 6, 2),"\
                "('B013', '倾城之恋', '张爱玲', '1943年', '上海文艺出版社', 'A14', 8, 6),"\
                "('B014', '哈姆莱特', '莎士比亚', '17世纪', '英国剧院出版社', 'U13', 7, 4),"\
                "('B015', '堂•吉诃德', '塞万提斯', '17世纪', '西班牙出版社', 'V14', 9, 7);"
        )

        cursor.execute(
        "INSERT INTO student (SID, PASSWORD, SNAME, DEPARTMENT, MAJOR, MAX) "\
        "VALUES  ('001', 'secret789', 'Tom Williams', 'Physics', 'Astrophysics', 5),"\
                "('002', 'pass456', 'Jane Smith', 'Mathematics', 'Applied Mathematics', 3); ")
        


        conn.commit()

    except Exception as e:
        print('Init fall')
        print(e)
    finally:
        if conn:
            conn.close()
        else:
            print('Database Connection Error.')