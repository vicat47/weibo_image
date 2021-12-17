#imports
import importlib

class DB:
    '''
    数据库类，用于执行一些通用的查询和增加操作，通过操作实例来访问数据库
    @author vicat
    '''
    def __init__(self, db_module, db_name):
        '''
        数据库模块选择，需要传入模块名供import
        @param db_module 数据库模块名
        @param db_name 数据库名，对于 sqlite 为文件名
        '''
        self.__db_module = self.dynamic_import(db_module)
        self.__db_name = db_name

    '''动态导入模块'''
    def dynamic_import(self, module):
        return importlib.import_module(module)

    '''获取查询结果，返回[{key:value}]'''
    def select_data(self, sql):
        with self.__db_module.connect(self.__db_name) as conn:
            c = conn.cursor()
            cursor = c.execute(sql)
            col_name_list = [tuple[0] for tuple in cursor.description]
            res = map(lambda x: dict(zip(col_name_list, x)), list(cursor))
            return res

    '''插入数据'''
    def insert_data(self, table_name, data):
        colum, value = '', ''
        for k,v in data.items():
            if v == None or v == '' or v == 'None' or k == 'id':
                continue
            colum += '%s,' % (k)
            if isinstance(v, int):
                value += '%d,' % (v)
            elif isinstance(v, str) :
                value += '"%s",' % (v)
            else:
                value += '"%s",' % (str(v))
        colum = colum[0:-1]
        value = value[0:-1]
        insert_sql = "insert into '%s' (%s) VALUES (%s)"
        with self.__db_module.connect(self.__db_name) as conn:
            c = conn.cursor()
            try:
                cursor = c.execute(insert_sql % (table_name, colum, value))
                conn.commit()
                return cursor.lastrowid
            except BaseException as e:
                print('插入失败')
    
    def update_data(self, table_name:str, condition:dict, data:dict):
        update_value, condition_str = '', ''
        update_sql = 'UPDATE %s SET %s WHERE %s'
        for k,v in condition.items():
            if v == None:
                continue
            condition_str += '%s=' % (k)
            if isinstance(v, int):
                condition_str += '%d and ' % (v)
            elif isinstance(v, str) :
                condition_str += '"%s" and ' % (v)
            else:
                condition_str += '"%s" and ' % (str(v))
        condition_str = condition_str[0:-4]
        for k,v in data.items():
            if v == None:
                continue
            update_value += '%s=' % (k)
            if isinstance(v, int):
                update_value += '%d, ' % (v)
            elif isinstance(v, str) :
                update_value += '"%s", ' % (v)
            else:
                update_value += '"%s", ' % (str(v))
        update_value = update_value[0:-2] + " "
        print(update_sql % (table_name, update_value, condition_str))
        with self.__db_module.connect(self.__db_name) as conn:
            c = conn.cursor()
            cursor = c.execute(update_sql % (table_name, update_value, condition_str))
            conn.commit()
            return cursor.lastrowid

    def delete_data(self, table_name, data):
        del_value = ''
        for k,v in data.items():
            if v == None:
                continue
            del_value += '%s=' % (k)
            if isinstance(v, int):
                del_value += '%d and ' % (v)
            elif isinstance(v, str) :
                del_value += '"%s" and ' % (v)
            else:
                del_value += '"%s" and ' % (str(v))
        del_value = del_value[0:-4]
        delete_sql = 'DELETE FROM %s WHERE %s'
        with self.__db_module.connect(self.__db_name) as conn:
            c = conn.cursor()
            cursor = c.execute(delete_sql % (table_name, del_value))
            conn.commit()
            return cursor.lastrowid

    def execute_sql(self, file):
        import re
        sqlist = []
        with open(file, encoding='utf-8', mode='r') as f:
            sqlist = f.read().split(';')[:-1]
        with self.__db_module.connect(self.__db_name) as conn:
            c = conn.cursor()
            for s in sqlist:
                s = re.sub(r'\n\s*', '', s)
                s = re.sub(r'\s+', ' ', s)
                s += ';'
                c.execute(s)
            conn.commit()

    def create_table(self, sql):
        with self.__db_module.connect(self.__db_name) as conn:
            c = conn.cursor()
            c.execute(sql)
            conn.commit()

if __name__ == '__main__':
    db = DB('sqlite3', 'my_fund.db')
    db.execute_sql('./db.sql')