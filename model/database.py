'''
所有有关数据库的操作全部集中在这个文件中
'''
import time
import pymysql


CONFIG = {
    "host": 'localhost',
    "user": 'root',
    "pwd": '123456',
    'db': 'Library'
}

# 检查注册信息
def check_user_info(info: dict) -> dict:
    '''
    info = {
            'SID': self.accountInput.text(),
            'PASSWORD': self.passwordInput.text(),
            'REPASSWORD': self.repPasswordInput.text(),
            'SNAME': self.nameInput.text(),
            'DEPARTMENT': self.deptInput.text(),
            'MAJOR': self.majorInput.text(),
            'MAX': self.maxNumInput.text(),
            'PUNISHED': 0
        }
    返回 ans = {
        'res':'fail|seccuss',
        'reason':''
    }
    '''
    ans = {
        'res':'fail',
        'reason':''
    }
    if len(info['SID']) > 15:
        ans['reason'] = 'ID长度超过15'
        return ans
    if not info['SID'].isalnum():
        ans['reason'] = 'ID存在非法字符'
        return ans
    if info['PASSWORD'] != info['REPASSWORD']:
        ans['reason'] = '两次输入密码不一致'
        return ans
    if not info['MAX'].isdigit():
        ans['reason'] = '最大数量输入含有非法字符'
        return ans
    if int(info['MAX']) > 10:
        ans['reason'] = '最多只能借阅10本书'
        return ans
    if len(info['DEPARTMENT']) > 20:
        ans['reason'] = '学院名称超过20'
        return ans
    if len(info['MAJOR']) > 20:
        ans['reason'] = '专业名称超过20'
        return ans
    ans['res'] = 'seccuss'
    return ans

# 去掉字符串末尾的0
def remove_blank(val):
    if type(val) is not str:
        return val
    while len(val) != 0 and val[-1] == ' ':
        val = val[:-1]
    return val


# 把book元组转换为list
def tuple_to_list(val: list):
    '''
    传入tuple列表把里面的tuple都转换为list同时去掉字符串里的空格
    '''
    ans = []
    for tuple_ in val:
        temp = []
        for item in tuple_:
            temp.append(item)
            if type(temp[-1]) is str:
                temp[-1] = remove_blank(temp[-1])
        ans.append(temp)
    return ans


# 将元组列表转换为字典
def convert(val: list):
    if len(val) == 0:
        return None
    val = val[0]
    # 如果是学生
    if len(val) == 5:
        ans = {
            'class': 'stu',
            'SID': remove_blank(val[0]),
            'SNAME': remove_blank(val[1]),
            'DEPARTMENT': remove_blank(val[2]),
            'MAJOR': remove_blank(val[3]),
            'MAX': val[4]
        }
    else:
        ans = {
            'class': 'admin',
            'AID': remove_blank(val[0])
        }
    return ans


# 将日期延后两个月
def postpone(start: str):
    temp = start.split('-')
    temp[0] = int(temp[0])
    temp[1] = int(temp[1])
    temp[2] = int(temp[2])
    temp[1] += 2
    if temp[1] > 12:
        temp[1] -= 12
        temp[0] += 1
    ans = '{:d}-{:0>2d}-{:0>2d}-{}'.format(temp[0], temp[1], temp[2], temp[3])
    return ans


# 两个日期之间间隔的天数
def days_between(start: str, end: str):
    start = start.split('-')
    end = end.split('-')
    start[0] = int(start[0])
    start[1] = int(start[1])
    start[2] = int(start[2])

    end[0] = int(end[0])
    end[1] = int(end[1])
    end[2] = int(end[2])

    s = start[0]*365+start[1]*30+start[2]
    e = end[0]*365+end[1]*30+end[2]
    return e-s



# 注册
def signup(user_message: dict) -> bool:
    '''
    传入以下格式的字典
    user_message{
        'SID': str,
        'PASSWORD': str,
        'SNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
        'MAX': int
    }
    '''
    res = True
    conn = None
    try:  
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        cursor.execute('''
            SELECT *
            FROM student
            WHERE SID=%s
            ''', (user_message['SID']))
        if len(cursor.fetchall()) != 0:
            raise Exception('用户已存在!')
        sql = "INSERT INTO student VALUES('%s', '%s', '%s', '%s', '%s', %d)" % (  user_message['SID'],
                                                                        user_message['PASSWORD'],
                                                                        user_message['SNAME'],
                                                                        user_message['DEPARTMENT'],
                                                                        user_message['MAJOR'],
                                                                        user_message['MAX']
                                                                    )
        print(sql)
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print('Signup error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 登录
def signin(user_message: dict) -> dict:
    '''
    传入以下格式的字典
    user_message{
        'ID': str,
        'PASSWORD': str
    }
    如果管理员用户存在返回以下字典
    {
        'class': 'admin'
        'AID': str
    }
    如果学生用户存在返回以下格式的字典
    {
        'class': 'stu'
        'SID': str,
        'SNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
        'MAX': int
    }
    否则返回None
    '''
    ans = None
    conn = None
    try:
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd'],
            db = CONFIG['db']
        )
        cursor = conn.cursor()
        # 现在administrator表内匹配
        cursor.execute('''USE Library;''')
        cursor.execute('''
        SELECT AID
        FROM administrator
        WHERE AID=%s AND PASSWORD=%s
        ''', (
            user_message['ID'],
            user_message['PASSWORD']
        ))
        temp = cursor.fetchall()
        # 管理员表内没有找到则在student表内匹配
        if len(temp) == 0:
            cursor.execute('''
            SELECT SID, SNAME, DEPARTMENT, MAJOR, MAX
            FROM student
            WHERE SID=%s AND PASSWORD=%s
            ''', (
                user_message['ID'],
                user_message['PASSWORD']
            ))
            temp = cursor.fetchall()
        ans = temp
        conn.commit()
    except Exception as e:
        print('Signin error!')
        print(e)
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
            return
        return convert(ans)


# 更新学生信息
def update_student(user_message: dict) -> bool:
    '''
    传入字典格式如下
    user_message{
        'SID': str,
        'PASSWORD': str,
        'SNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
        'MAX': int
    }
    返回bool
    '''
    conn = None
    try:
        res = True
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd'],
            db = CONFIG['db']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        cursor.execute('''
            UPDATE student
            SET SNAME=%s, DEPARTMENT=%s, MAJOR=%s, MAX=%s
            WHERE SID=%s
            ''', (
                user_message['SNAME'],
                user_message['DEPARTMENT'],
                user_message['MAJOR'],
                user_message['MAX'],
                user_message['SID']
            ))
        if 'PASSWORD' in user_message:
            cursor.execute('''
            UPDATE student
            SET PASSWORD=%s
            WHERE SID=%s
            ''', (
                user_message['PASSWORD'],
                user_message['SID']
            ))
        conn.commit()
    except Exception as e:
        print('Update error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        else :
            print('Database Connection Error.')
        return res


# 获取学生信息
def get_student_info(SID: str) -> dict:
    '''
    传入SID
    返回stu_info{
        'class': stu,
        'SID': str,
        'SNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
        'MAX': int
    }
    '''
    conn = None
    try:
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        cursor.execute('''
            SELECT SID, SNAME, DEPARTMENT, MAJOR, MAX
            FROM student
            WHERE SID=%s
            ''', (SID))
        ans = cursor.fetchall()
    except Exception as e:
        print(e)
        print('get student info error')
    finally:
        if conn: 
            conn.close()
        return convert(ans)


# 查找学生
def search_student(info: str) -> list:
    '''
    传入SID或学生姓名进行查找
    返回[[SID, SNAME, DEPARTMENT, MAJOR, MAX],...]
    '''

    conn = None
    try:
        res = []
        val = info.split()
        val = [(i, '%'+i+'%') for i in val]
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        # 显示所有书信息
        if info == 'ID/姓名' or info == '':
            cursor.execute('''
            SELECT SID, SNAME, DEPARTMENT, MAJOR, MAX
            FROM student
            ''')
            res += cursor.fetchall()
        else:
            # 按条件查找
            for i in val:
                cursor.execute('''
                SELECT SID, SNAME, DEPARTMENT, MAJOR, MAX
                FROM student
                WHERE SID=%s OR SNAME LIKE %s
                ''', i)
                res += cursor.fetchall()
        res = list(set(res))
        temp = []
        for i in res:
            temp_ = []
            for j in i:
                temp_.append(remove_blank(j))
            temp.append(temp_)
        res = temp
    except Exception as e:
        print('Search student error!')
        print(e)
        res = []
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 删除学生信息
def delete_student(SID: str) -> bool:
    '''
    传入SID
    删除student表内记录,
    找出book表内所借的书强制还书
    删除log表内的记录
    '''
    conn = None
    try:
        res = True
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        # 先强制把书还掉
        cursor.execute('''
            SELECT BID
            FROM borrowing_book
            WHERE SID=%s
        ''', (SID))
        BID_list = cursor.fetchall()
        for BID in BID_list:
            return_book(BID, SID)
        # 再删除学生信息
        cursor.execute('''
            DELETE
            FROM student
            WHERE SID=%s
        ''', SID)
        cursor.execute('''
            DELETE
            FROM log
            WHERE SID=%s
            ''', SID)
        conn.commit()
    except Exception as e:
        print('delete book error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 获取学生的借书信息
def get_borrowing_books(ID: str, BID: bool = False) -> list:
    '''
    当BID为False以SID的方式查找否则以BID查找
    返回此学生在借的书籍列表信息
    [[SID, BID, BNAME, BORROW_DATE, DEADLINE, PUNISH, NUM],[...],....]
    '''
    conn = None
    try:
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        if ID == '' or ID == 'ID/姓名':
            cursor.execute('''
                SELECT SID, book.BID, BNAME, BORROW_DATE, DEADLINE, PUNISH, NUM
                FROM borrowing_book, book
                WHERE book.BID=borrowing_book.BID
            ''')
        elif BID:
            cursor.execute('''
                SELECT SID, book.BID, BNAME, BORROW_DATE, DEADLINE, PUNISH, NUM
                FROM borrowing_book, book
                WHERE book.BID=%s AND book.BID=borrowing_book.BID
            ''', (ID,))
        else:
            cursor.execute('''
                SELECT SID, book.BID, BNAME, BORROW_DATE, DEADLINE, PUNISH, NUM
                FROM borrowing_book, book
                WHERE SID=%s AND book.BID=borrowing_book.BID
            ''', (ID,))
        res = cursor.fetchall()
        temp = []
        for i in res:
            temp_ = []
            for j in i:
                temp_.append(remove_blank(j))
            temp.append(temp_)
        res = temp
    except Exception as e:
        print('get borrowing books error!')
        print(e)
        res = []
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 还书
def return_book(BID: str, SID: str) -> bool:
    '''
    传入BID, SID，删除borrowing_book表内的记录在log表内新建记录
    返回bool型
    '''
    conn = None
    try:
        res = True
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        # 先把借书日期，书本剩余数量，罚金等信息找出
        cursor.execute('''
        SELECT BORROW_DATE, NUM, PUNISH
        FROM book, borrowing_book
        WHERE SID=%s AND borrowing_book.BID=%s AND borrowing_book.BID=book.BID
        ''', (SID, BID))
        book_mes = cursor.fetchall()
        NUM = book_mes[0][1]
        BORROW_DATE = book_mes[0][0]
        PUNISH = book_mes[0][2]
        BACK_DATE = time.strftime("%Y-%m-%d-%H:%M")

        # book表内NUM加一
        cursor.execute('''
        UPDATE book
        SET NUM=%s
        WHERE BID=%s
        ''', (NUM+1, BID))

        # 从borrowing_book表内删除记录
        cursor.execute('''
        DELETE
        FROM borrowing_book
        WHERE SID=%s AND BID=%s
        ''', (SID, BID))

        # 将记录插入log表
        cursor.execute('''
        INSERT
        INTO log
        VALUES(%s, %s, %s, %s, %s)
        ''', (BID, SID, BORROW_DATE, BACK_DATE, PUNISH))
        conn.commit()
    except Exception as e:
        print('Return error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 交罚金
def pay(BID: str, SID: str, PUNISH: int) -> bool:
    '''
    传入BID, SID, PUNISH把当前数的DEADLINE往后延长两个月
    返回bool型
    '''
    conn = None
    try:
        res = True
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        # book表内NUM加一，删除borrowing_book表内的记录，把记录插入log表
        cursor.execute('''
            UPDATE borrowing_book
            SET DEADLINE=%s, PUNISH=%s
            WHERE BID=%s AND SID=%s
            ''', (postpone(time.strftime('%Y-%m-%d-%H:%M')), PUNISH, BID, SID))
        conn.commit()
    except Exception as e:
        print('Pay error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 获取历史记录
def get_log(ID: str, BID: bool = False) -> list:
    '''
    传入SID
    返回[[SID, BID, BNAME, BORROW_DATE, BACK_DATE, PUNISHED],...]
    '''
    conn = None
    try:
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        if ID == '' or ID == 'ID/姓名':
            cursor.execute('''
                SELECT SID, book.BID, BNAME, BORROW_DATE, BACK_DATE, PUNISHED
                FROM log, book
                WHERE book.BID=log.BID
                ORDER BY BACK_DATE
            ''')
        elif BID:
            cursor.execute('''
                SELECT SID, book.BID, BNAME, BORROW_DATE, BACK_DATE, PUNISHED
                FROM log, book
                WHERE log.BID=%s AND book.BID=log.BID
                ORDER BY BACK_DATE
            ''', (ID,))
        else:
            cursor.execute('''
                SELECT SID, book.BID, BNAME, BORROW_DATE, BACK_DATE, PUNISHED
                FROM log, book
                WHERE SID=%s AND book.BID=log.BID
                ORDER BY BACK_DATE
            ''', (ID,))
        res = cursor.fetchall()
    except Exception as e:
        print('get log error!')
        print(e)
        res = []
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        temp = []
        for i in res:
            temp_ = []
            for j in i:
                temp_.append(remove_blank(j))
            temp.append(temp_)
        return temp


# 加入新书
def new_book(book_info: dict) -> bool:
    '''
    传入以下格式的字典
    book_msg{
        'BID': str,
        'BNAME': str,
        'AUTHOR': str,
        'PUBLICATION_DATE': str,
        'PRESS': str,
        'POSITION': str,
        'SUM': int,
        'CLASSIFICATION': str
    }
    返回bool
    '''
    res = True
    try:
        conn = None
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        cursor.execute('''
            SELECT *
            FROM book
            WHERE BID=%s
            ''', (book_info['BID']))
        if len(cursor.fetchall()) != 0:
            raise Exception('书ID已存在!')
        # 插入新书
        cursor.execute('''
        INSERT
        INTO book
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            book_info['BID'],
            book_info['BNAME'],
            book_info['AUTHOR'],
            book_info['PUBLICATION_DATE'],
            book_info['PRESS'],
            book_info['POSITION'],
            book_info['SUM'],
            book_info['SUM']
        ))

        # 处理书本分类
        classifications = book_info['CLASSIFICATION']
        classifications = classifications.split()
        classifications = list(set(classifications))
        classifications = [(book_info['BID'], i) for i in classifications]
        # 插入分类
        cursor.executemany('''
        INSERT
        INTO classification
        VALUES(%s, %s)
        ''', classifications)

        conn.commit()
    except Exception as e:
        print('add book error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 获取新书详细信息
def get_book_info(BID: str) -> dict:
    '''
    传入BID
    返回book_msg{
        'BID': str,
        'BNAME': str,
        'AUTHOR': str,
        'PUBLICATION_DATE': str,
        'PRESS': str,
        'POSITION': str,
        'SUM': int,
        'NUM': int,
        'CLASSIFICATION': str
    }
    '''
    try:
        conn = None
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        # 获取book表内的书本信息
        cursor.execute('''
            SELECT *
            FROM book
            WHERE BID=%s
            ''', (BID))
        res = cursor.fetchall()
        if len(res) == 0:
            raise Exception('查无此书')

        # 获取分类
        cursor.execute('''
        SELECT CLASSIFICATION
        FROM classification
        WHERE BID=%s
        ''', (BID))
        CLASSIFICATION = ''
        for i in cursor.fetchall():
            CLASSIFICATION += (remove_blank(i[0]) + ' ')
        # 把列表转换为字典
        res = list(res[0])
        res.append(CLASSIFICATION)
        key_list = ['BID', 'BNAME', 'AUTHOR', 'PUBLICATION_DATE', 'PRESS', 'POSITION', 'SUM', 'NUM', 'CLASSIFICATION']
        ans = {}
        for i, key in zip(res, key_list):
            ans[key] = i
            if type(i) is str:
                ans[key] = remove_blank(i)
        res = ans
    except Exception as e:
        print('get book info error!')
        print(e)
        res = None
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 更新书籍信息
def update_book(book_info: dict) -> bool:
    '''
    传入以下格式的字典
    book_msg{
        'BID': str,
        'BNAME': str,
        'AUTHOR': str,
        'PUBLICATION_DATE': str,
        'PRESS': str,
        'POSITION': str,
        'SUM': int,
        'NUM': int,
        'CLASSIFICATION': str
    }
    返回bool
    '''
    conn = None
    try:
        res = True
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd'],
            db = CONFIG['db']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        # 更新book表
        cursor.execute('''
            UPDATE book
            SET BNAME=%s, AUTHOR=%s, PUBLICATION_DATE=%s, PRESS=%s, POSITION=%s, SUM=%d, NUM=%d
            WHERE BID=%s
            ''', (
                book_info['BNAME'],
                book_info['AUTHOR'],
                book_info['PUBLICATION_DATE'],
                book_info['PRESS'],
                book_info['POSITION'],
                book_info['SUM'],
                book_info['NUM'],
                book_info['BID']
            ))

        # 更新classification表
        cursor.execute('''
        DELETE
        FROM classification
        WHERE BID=%s''', (book_info['BID']))
        # 处理书本分类
        classifications = book_info['CLASSIFICATION']
        classifications = classifications.split()
        classifications = list(set(classifications))
        classifications = [(book_info['BID'], i) for i in classifications]
        # 插入分类
        cursor.executemany('''
        INSERT
        INTO classification
        VALUES(%s, %s)
        ''', classifications)

        conn.commit()
    except Exception as e:
        print('Update book error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        return res


# 删除书籍
def delete_book(BID: str) -> bool:
    '''
    传入BID
    返回bool
    会删除book，borrowing_book，log, classification 表内所有对应的记录
    '''
    try:
        res = True
        conn = None
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')
        cursor.execute('''
            DELETE
            FROM book
            WHERE BID=%s
        ''', BID)
        cursor.execute('''
            DELETE
            FROM borrowing_book
            WHERE BID=%s
        ''', BID)
        cursor.execute('''
            DELETE
            FROM log
            WHERE BID=%s
        ''', BID)
        cursor.execute('''
            DELETE
            FROM classification
            WHERE BID=%s
            ''', BID)
        conn.commit()
    except Exception as e:
        print('delete book error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 搜索书籍
def search_book(info: str, restrict: str, SID: str = '') -> list:
    '''
    传入搜索信息，并指明BID或AUTHOR或PRESS或BNAME或CLASSIFYICATION进行查找，如果传入SID则匹配这个学生的借书状态
    返回[[BID, BNAME, AUTHOR, PUBLICATION_DATE, PRESS, POSITION, SUM, NUM, CLASSIFICATION, STATE],...]
    '''
    conn = None
    try:
        res = []
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd'],
            db = CONFIG['db']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')

        # 显示所有书信息
        if info == 'ID/书名/作者/出版社' or info == '':
            cursor.execute('''
            SELECT *
            FROM book
            ''')
            res = tuple_to_list(cursor.fetchall())
        elif restrict != 'BID' and restrict != 'CLASSIFICATION':
            # AUTHOR或PRESS或BNAME
            cursor.execute(f'''
            SELECT *
            FROM book
            WHERE {restrict} LIKE %s
            ''', ('%' + info + '%'))
            res = tuple_to_list(cursor.fetchall())
        elif restrict == 'BID':
            # BID
            cursor.execute('''
            SELECT *
            FROM book
            WHERE BID = %s
            ''', (info))
            res = tuple_to_list(cursor.fetchall())
        elif restrict == 'CLASSIFICATION':
            # 通过分类搜书
            cursor.execute('''
            SELECT BID
            FROM classification
            WHERE CLASSIFICATION = %s
            ''', (info))
            for BID in cursor.fetchall():
                cursor.execute('''
                SELECT *
                FROM book
                WHERE BID = %s
                ''', (BID[0]))
                res.append(tuple_to_list(cursor.fetchall())[0])
        # 把分类搜出来
        for book_info in res:
            CLASSIFICATIONS = ''
            BID = book_info[0]
            cursor.execute('''
            SELECT CLASSIFICATION
            FROM classification
            WHERE BID = %s
            ''', (BID))
            for classification in cursor.fetchall():
                CLASSIFICATIONS += (remove_blank(classification[0]) + ' ')
            book_info.append(CLASSIFICATIONS)

        # 匹配学生信息判断每一本书是否可借
        if SID != '':
            # 获得学生最大借书数
            cursor.execute('''
            SELECT MAX
            FROM student
            WHERE SID=%s
            ''', (SID))
            max_num = cursor.fetchall()[0][0]
            # 获取已经借阅的书的列表
            borrowing_book = get_borrowing_books(SID)
            # 判断是否有罚金
            punish = False
            for i in borrowing_book:
                if i[4] < time.strftime("%Y-%m-%d-%H:%M"):
                    punish = True
                    break
            for book in res:
                # 有罚金没交
                if punish:
                    book.append('未交罚金')
                    continue
                # 如果已经借的书达到上限就不再可借
                if len(borrowing_book) >= max_num:
                    book.append('借书达上限')
                    continue
                if book[-2] == 0:
                    book.append('没有剩余')
                    continue
                # 判断是否有此书
                for borrow in borrowing_book:
                    if book[0] == borrow[1]:
                        book.append('已借此书')
                        break
                if book[-1] != '已借此书':
                    book.append('借书')
    except Exception as e:
        print('Search error!')
        print(e)
        res = []
    finally:
        if conn: 
            conn.close()
        return res


# 借书
def borrow_book(BID: str, SID: str) -> bool:
    '''
    传入BID和SID
    返回bool
    book的NUM减一
    在borrowing_book表内新建记录
    '''
    try:
        res = True
        conn = None
        conn = pymysql.connect(
            host = CONFIG['host'], 
            user = CONFIG['user'], 
            password = CONFIG['pwd']
        )
        cursor = conn.cursor()
        cursor.execute('''USE Library;''')

        # 先把借书日期，书本剩余数量，罚金等信息找出
        cursor.execute('''
        SELECT NUM
        FROM book
        WHERE BID=%s
        ''', (BID))
        book_mes = cursor.fetchall()
        # print(book_mes)
        NUM = book_mes[0][0]
        BORROW_DATE = time.strftime("%Y-%m-%d-%H:%M")
        DEADLINE = postpone(BORROW_DATE)

        # book表内NUM减一
        cursor.execute('''
        UPDATE book
        SET NUM=%s
        WHERE BID=%s
        ''', (NUM-1, BID))

        # 新建borrowing_book表内的记录
        cursor.execute('''
        INSERT INTO borrowing_book (BID, SID, BORROW_DATE, DEADLINE, PUNISH)
        VALUES (%s, %s, %s, %s, 0)
        ''', (BID, SID, BORROW_DATE, DEADLINE))
        conn.commit()

    except Exception as e:
        print('borrow error!')
        print(e)
        res = False
    finally:
        if conn: 
            conn.close()
        else:
            print('Database Connection Error.')
        return res


# 密码   为了调试方便就先不加密了
def encrypt(val):
    import hashlib
    h = hashlib.sha256()
    password = val
    h.update(bytes(password, encoding='UTF-8'))
    result = h.hexdigest()
    # 注释下面一行即可加密
    result = val
    return result

