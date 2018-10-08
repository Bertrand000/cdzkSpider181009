#!/usr/bin/env python
# encoding: utf-8
from cdzk.dao.model.cdzk_basedata_model import *

'''

@author: Mr.Chen
@file: DB_service.py
@time: 2018/9/20 14:39

'''

class  DBService():
    def cdzk_basedata_save(self,Cdzk):
        if Cdzk:
            replace_data = \
                (Cdzk.schoolName,Cdzk.province,Cdzk.type,Cdzk.recruitStudentsOrder,Cdzk.sourceId)

            replace_sql = '''REPLACE INTO
                                school_base_data(school_name,province,type,recruit_students_order,source_id)
                                VALUES(%s,%s,%s,%s,%s)'''

            try:
                print("获取到数据：")
                print(Cdzk)
                self.db_cursor.execute(replace_sql, replace_data)
                self.db.commit()
            except Exception as err:
                print("插入数据库出错")
                print("获取到数据：")
                print(replace_data)
                print("插入语句：" + self.db_cursor._last_executed)
                self.db.rollback()
                print(err)
        else:
            print("数据格式不正确")
