#!/usr/bin/env python
# encoding: utf-8
'''

@author: Mr.Chen
@file: cdzk_basedata_model.py
@time: 2018/9/20 10:33

'''

class Cdzk(object):
    def __init__(self):
        # id
        self.id = None
        # 学校名
        self.schoolName = None
        # 省份
        self.province = None
        # 科类
        self.type = None
        # 招生批次
        self.recruitStudentsOrder = None
        # 网站数据id
        self.sourceId = None


    def getId(self):
        return self.id

    def getSchoolName(self):
        return self.schoolName

    def setSchoolName(self, value):
        self.schoolName = value

    def delSchoolName(self):
        del self.schoolName

    def setProvince(self, value):
        self.province = value

    def getprovince(self):
        return self.province

    def delProvince(self):
        del self.province

    def getType(self):
        return self.type

    def setType(self, value):
        self.type = value

    def delType(self):
        del self.type

    def getRecruitStudentsOrder(self):
        return self.getRecruitStudentsOrder

    def setRecruitStudentsOrder(self, value):
        self.recruitStudentsOrder = value

    def delRecruitStudentsOrder(self):
        del self.recruitStudentsOrder

    def getSourceId(self):
        return self.getSourceId

    def setSourceId(self, value):
        self.sourceId = value

    def delSourceId(self):
        del self.sourceId

    def __str__(self):
        return "id:" + self.id + ",name:" + self.schoolName + ",province:" + self.province + ",type" + self.type + ",recruitStudentsOrder:" + \
               self.recruitStudentsOrder + ",sourceId:" + self.sourceId
