# -*- coding: utf-8 -*-
import requests
import http.cookiejar as cookielib
import configparser
import json
import jsonpath
import re
import pymysql
from bs4 import BeautifulSoup
from cdzk.my_util import *

# 获取配置
cfg = configparser.ConfigParser()
cfg.read("config.ini")

class GetZK():
    session = None
    config = None
    def __init__(self, threadID=1, name=''):
        # 获取配置
        self.config = cfg

        # 初始化session
        requests.adapters.DEFAULT_RETRIES = 5
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(filename='cookie')
        self.session.keep_alive = False
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            print('Cookie 未能加载')
        finally:
            pass
        # test
        # 初始化数据库连接
        try:
            db_host = self.config.get("db", "host")
            db_port = int(self.config.get("db", "port"))
            db_user = self.config.get("db", "user")
            db_pass = self.config.get("db", "password")
            db_db = self.config.get("db", "db")
            db_charset = self.config.get("db", "charset")
            self.db = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_db,
                                      charset=db_charset)
            self.db_cursor = self.db.cursor()
        except Exception as err:
            print("请检查数据库配置")
    # 模拟登陆
    def login(self):

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
            ,"origin":"https://www.cdzk.cn"
            ,"X-Requested-With": "XMLHttpRequest"
            ,"referer": "https://www.cdzk.cn/HistoryData/SpecialtyEnrollDiff"
            ,"cookie": "Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1539414959; ASP.NET_SessionId=ybacj05qi1secggwtdm43h5g; LoginName=13551031630; last_card=868916619; canRedir=no; __RequestVerificationToken=3-oDEYbfBVpAnYM68iAENleV2L2-ho3zXmy1iS2lnDgv15738ncYKqI3Yyjmz10j0bd2NNlbaNaCdqdSyIAqNN2eTSeaCoKrI_04aLI-f701; .ASPXAUTH=01A64AC3AC1FEF522B99998DF7577BCF477E2CA0663DDAF607B5BFD6D835A1E6C7B07F1FE56A1606FAB89C38EA3FCE843EE34C97171E4AE5943C82B29CA959E2EF38A3CCB8E38509780CAC60A81F2FDEA1A0E4EF389BF20D05397C3CB1DEC97822BBFB5A535FA24FFF781F19CE57B309; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM5NTcxODY0LCJJYXQiOjE1Mzk1MzU4NjQsIkp0aSI6Ijk4MzgyMTg3NyJ9.HQ2L84EeW70AmKkz5ySI2wEOgCQ8zg37dRYBsgoohx0; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiNWU3ZjdkMWQtZjRkZi00NGYyLTgzYzgtMjZjZDE5NDhlNjU3IiwibmJmIjoxNTM5NTM1ODY1LCJleHAiOjE1NDIxMjc4NjUsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.nmw51IPR8anoU0nztomDha6ZOiA4X7rGuD0yJdKG_6U; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1539535914|1539532231; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1539535915"
        }
        data = {
            'UserID': '13551031630',
            'loginPassword': 'scsc1234'
        }
        login_page = self.session.post('https://www.cdzk.cn/HistoryData/GetSpecialtyEnrollDiff?collegeHistoryID=47&pageSize=10000&currentPage=1', headers=headers, timeout=35)
        print(str(self.session.cookies.values))
        self.session.cookies.save()
    # 处理json 获取base_data
    def json_data(self):
        replace_sql = '''REPLACE INTO
                                                  base_data(collegeHistoryId,gradeDiffLevel,order_1,subject_1,collegeCode,collegeName,province)
                                                  VALUES(%s,%s,%s,%s,%s,%s,%s)'''
        base_data_object = open("json_data.txt", "r", encoding='utf-8')
        try:
            data_context = base_data_object.read()
        finally:
            base_data_object.close()
        data_context = re.sub('\'', '\"', data_context)
        unicodestr = json.loads(str(data_context))
        data = jsonpath.jsonpath(unicodestr,"$.data.items")
        try:
            for d in data[0] :
                print("获取到数据：")
                test = tuple(d.values())
                self.db_cursor.execute(replace_sql, test)
                self.db.commit()
        except Exception as err:
            print("插入数据库出错")
            print("获取到数据：")
            self.db.rollback()
            print(err)
    # 分配任务
    def manage(self):
        base_data_object = open("json_data.txt","r",encoding='utf-8')
        try:
            data_context = base_data_object.read()
        finally:
            base_data_object.close()
        data_context = re.sub('\'', '\"', data_context)
        unicodestr = json.loads(str(data_context))
        id_list = jsonpath.jsonpath(unicodestr, "$.data.items[*].collegeHistoryId")
        # 登陆一次首页，获取cookie
        self.login()
        for id in id_list:
            # self.get_enrollDetail(id)
            self.get_specialtyEnrollDiff(id)
            # self.get_collegeenrolldiff(id)

        print("---------------------------------------------------------------------------------------------------------h")
        print("数据爬取完成")
        # 错误状态码： 0. base_data 1.gradeDiffs 出错 2.空数据 3.获取接口失败
    def get_specialtyEnrollDiff(self,id):
        specialtyEnrollDiff_base_data_sql = '''REPLACE INTO
                                          specialtyEnrollDiff_base(SpecialtyHistoryID,SpecialtyCode,SpeicaltyName,CollegeHistoryID,SpecComment)
                                          VALUES(%s,%s,%s,%s,%s)'''
        specialtyEnrollDiff_gradeDiffs_data_sql = '''REPLACE INTO
                                                  specialtyEnrollDiff_gradeDiffs(SpecialtyHistoryID,SpecialtyGradeDiffYear,MatricGrade,SpecialtyGradeDiff,AverageGrade,AverageGradeDiff,MatricGradePosition,AverageGradePosition)
                                                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
        specialtyEnrollDiff_bad_data_sql = '''REPLACE INTO
                                                  specialtyEnrollDiff_bad(bad_data_value,bad_status)
                                                  VALUES(%s,%s)'''
        specialtyEnrollDiff_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
            ,"origin":"https://www.cdzk.cn"
            ,"X-Requested-With": "XMLHttpRequest"
            ,"referer": "https://www.cdzk.cn/HistoryData/SpecialtyEnrollDiff"
            # ,"cookie": "Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1539414959; ASP.NET_SessionId=ybacj05qi1secggwtdm43h5g; LoginName=13551031630; last_card=868916619; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMmMzMzNiYzktNDVhYS00NmJhLTlhODMtNzMxMWI2YzdhYzNmIiwibmJmIjoxNTM5NDE0OTgxLCJleHAiOjE1NDIwMDY5ODEsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.mPuRYftheovplW-hAc3wq7_MXH21CHBRZ-RjkR81Suo; canRedir=no; __RequestVerificationToken=3-oDEYbfBVpAnYM68iAENleV2L2-ho3zXmy1iS2lnDgv15738ncYKqI3Yyjmz10j0bd2NNlbaNaCdqdSyIAqNN2eTSeaCoKrI_04aLI-f701; .ASPXAUTH=A7AFA76DFE9650189ABD1069403C619D640892870788BA8BCC481385E073410835D7CD53A71663BCA03EC075FE61B3E7E5098D7E035EB465A8F43290226E460FBDE1871EF88C2AEC99CF4BEA708B6069BA130A1926BB29ACA2FF1FDDB005384D9E0A14A4F462C61986CBB63C1A2EEBF9; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1539532963|1539532231; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1539532965; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM5NTY4OTYzLCJJYXQiOjE1Mzk1MzI5NjMsIkp0aSI6IjEyOTA4NzkxODQifQ.7io9S4x4Z9Ngk2zk62LFrXSuds5zHpz6MO8fhiagqQs"
            ,"cookie": self.session.cookies.values()
        }
        specialtyEnrollDiff_url = "https://www.cdzk.cn/HistoryData/GetSpecialtyEnrollDiff?collegeHistoryID=" + str(id) + "&pageSize=10000&currentPage=1"
        try:
            resp = self.session.post(specialtyEnrollDiff_url, headers=specialtyEnrollDiff_headers,timeout=35)
            print(self.session.cookies)
            self.session.cookies.save()
        except Exception as err:
            print("读取接口失败 数据id：" + str(id))
            self.db_cursor.execute(specialtyEnrollDiff_bad_data_sql, (str(id), "3"))
            self.db.commit()
            print(err)
        unicodestr = json.loads(str(resp.text))
        data = jsonpath.jsonpath(unicodestr, "$.data")
        if not data[0]:
            print("data数据为空")
            self.db_cursor.execute(specialtyEnrollDiff_bad_data_sql,(id,"2"))
            self.db.commit()
            data[0] = '''[{
                "SpecialtyHistoryID": %s,
                "SpecialtyCode": "无数据",
                "SpeicaltyName": "无数据",
                "CollegeHistoryID": %s,
                "SpecComment": "无数据",
                "GradeDiffs": [{
                    "SpecialtyHistoryID": %s,
                    "SpecialtyGradeDiffYear": "2017",
                    "MatricGrade": "无数据",
                    "SpecialtyGradeDiff": "无数据",
                    "AverageGrade": "无数据",
                    "AverageGradeDiff": "无数据",
                    "MatricGradePosition": "无数据",
                    "AverageGradePosition": "无数据"
                }, {
                    "SpecialtyHistoryID": %s,
                    "SpecialtyGradeDiffYear": "2016",
                    "MatricGrade": "无数据",
                    "SpecialtyGradeDiff": "无数据",
                    "AverageGrade": "无数据",
                    "AverageGradeDiff": "无数据",
                    "MatricGradePosition": "无数据",
                    "AverageGradePosition": "无数据"
                }]
            }]'''%(str(id),str(id),str(id),str(id))
        data_list = json.loads(data[0])
        for base_data in data_list:
            specialtyEnrollDiff_base_data = (base_data['SpecialtyHistoryID'],base_data['SpecialtyCode'],base_data['SpeicaltyName'],base_data['CollegeHistoryID'],base_data['SpecComment'])
            try:
                print("获取到数据：")
                print(base_data)
                self.db_cursor.execute(specialtyEnrollDiff_base_data_sql, specialtyEnrollDiff_base_data)
                self.db.commit()
            except Exception as err:
                print("插入数据库出错")
                self.db.rollback()
                self.db_cursor.execute(specialtyEnrollDiff_bad_data_sql,(str(id) + "内容 获取到的数据:" + str(data),"0"))
                print(err)
            for i,gradeDiffs_data in enumerate(base_data['GradeDiffs']):
                if gradeDiffs_data['SpecialtyHistoryID']:
                    specialtyEnrollDiff_gradeDiffs_data = (gradeDiffs_data['SpecialtyHistoryID'],gradeDiffs_data['SpecialtyGradeDiffYear'],gradeDiffs_data['MatricGrade'],gradeDiffs_data['SpecialtyGradeDiff'],gradeDiffs_data['AverageGrade'],gradeDiffs_data['AverageGradeDiff'],gradeDiffs_data['MatricGradePosition'],gradeDiffs_data['AverageGradePosition'])
                else:
                    specialtyEnrollDiff_gradeDiffs_data = (base_data['SpecialtyHistoryID'],2017 if i==0 else 2016,"无数据","无数据","无数据","无数据","无数据","无数据")
                try:
                    print("获取到数据：")
                    print(base_data)
                    self.db_cursor.execute(specialtyEnrollDiff_gradeDiffs_data_sql, specialtyEnrollDiff_gradeDiffs_data)
                    self.db.commit()
                except Exception as err:
                    print("插入数据库出错")
                    self.db.rollback()
                    self.db_cursor.execute(specialtyEnrollDiff_bad_data_sql,( "错误数据内容: " + str(specialtyEnrollDiff_gradeDiffs_data),"1"))
                    print(err)
    def get_enrollDetail(self, id):
        if not id:
            print("id 不能为空")
            return None
        enrollDetail_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
            , "authority": "m.in985.com"
            , "method": "GET"
            , "path": "/api/v1/history/college/enrollDetail/47"
            , "scheme": "https"
            , "accept": "application/json, text/javascript, */*; q=0.01"
            , "accept-encoding": "gzip, deflate, br"
            , "accept-language": "zh-CN,zh;q=0.8"
            ,
            "authorization": "eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU"
            , "origin": "https://www.cdzk.cn"
            , "referer": "https://www.cdzk.cn/historydata/collegeenrolldetail?collegeHistoryID=" + str(id) + "&code=0"
            ,"cookie": "ASP.NET_SessionId=5fgkdjorro1rlo1s2zbfavpx; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMDRlNmVjM2MtODVlNS00YTFhLTljZTktYjJkZTMwMWMxY2Y5IiwibmJmIjoxNTM4MTQzODk3LCJleHAiOjE1NDA3MzU4OTcsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.fU2WfMJXtjRCANebB6xWTBIdtywBsvfKZ0ejgejm3fY; __RequestVerificationToken=wuQr51hVLBonjGVTKDPcmUga5Hx67udr4It5E1utghKCdkWyXe4l2FRv0X2x1kXSBlg498jGn7QgHx4PVR_pXb-VGZQtKcO0710xGS_zryE1; Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1538143778; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1538238276; LoginName=13551031630; .ASPXAUTH=58998A48ABC89178205192365B5BB65C3D16BDBC9516D915EB7E0462B6BD5EC96082717508163A6660A8FB2F1AF548EC574E2F49621F9C260BCB03E670A43BA7540B33DEE7CCFA8B60418CA2C64FA6392AF61B5BA60E38756BF6C4C0EC1DA69260ACB290D2E2430B532F0FEF21F46045; last_card=868916619; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1538239474|1538236939"
        }
        enrollDetail_url = "https://m.in985.com/api/v1/history/college/enrollDetail/" + str(id)
        bad_data_sql = '''REPLACE INTO
                                                  bad_data(nodata_source_id,error_value)
                                                  VALUES(%s,%s)'''
        replace_sql = '''REPLACE INTO
                                          enroll_detail(source_id,year,real_recruit_total,first_wish_total,enroll_property,first_wish_suc_total,second_wish_suc_total)
                                          VALUES(%s,%s,%s,%s,%s,%s,%s)'''
        try:
            resp = self.session.get(enrollDetail_url, headers=enrollDetail_headers,timeout=35)
            unicodestr = json.loads(str(resp.text))
            data_list = jsonpath.jsonpath(unicodestr, "$.data.*")
            test = len(str(unicodestr))
            if len(str(unicodestr)) == 45:
                print("id:"+ str(id) + "无数据")
                errdata_model = (id,str(unicodestr))
                try:
                    self.db_cursor.execute(bad_data_sql,errdata_model)
                    self.db.commit()
                except Exception as err:
                    print("插入数据库出错")
                    print("获取到数据：")
                    self.db.rollback()
                    print(err)
                return None
            for data in data_list:
                try:
                    print("获取到数据：")
                    print(data)
                    self.db_cursor.execute(replace_sql, tuple(data.values()))
                    self.db.commit()
                except Exception as err:
                    print("插入数据库出错")
                    print("获取到数据：")
                    print(data)
                    self.db.rollback()
                    print(err)
        except Exception as err:
            print("获取接口数据失败")
            print("数据id:" + str(id))
            print(err)

    # 获取高校录取分数方法 HTML解析
    # 错误状态码 0.读取出的数据格式超出预料 1.网络接口异常
    # data = ('年份','调档分','平均分','省控线','调档 本一线差','平均 本一线差','调档分档次','平均分档次')
    def get_collegeenrolldiff(self,id):
        collegeenrolldiff_data_sql = '''REPLACE INTO
                                                          college_enroll_diff(year,diaodangfen,pinjunfen,shengkongxian,diaodangbenyixiancha,pinjunbenyixiancha,diaodangfenweici,pinjunfenweici,collegeHistoryId)
                                                          VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        collegeenrolldiff_bad_data_sql = '''REPLACE INTO
                                                          college_enroll_diff_bad(source_id,bad_value,bad_statue)
                                                          VALUES(%s,%s,%s)'''
        collegeenrolldiff_heads = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
            ,"cookie": "Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1539414959; ASP.NET_SessionId=ybacj05qi1secggwtdm43h5g; LoginName=13551031630; last_card=868916619; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMmMzMzNiYzktNDVhYS00NmJhLTlhODMtNzMxMWI2YzdhYzNmIiwibmJmIjoxNTM5NDE0OTgxLCJleHAiOjE1NDIwMDY5ODEsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.mPuRYftheovplW-hAc3wq7_MXH21CHBRZ-RjkR81Suo; __RequestVerificationToken=-gRUozZYn5BW7K6sRk3F-rre9mNR79DNs2TafpqaGEL8KeyXIHKKksy1AxFhaCE2BJVahLxOeYUi_zyssNb5TRypeE-lL0THzW7VLp7tls41; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1539516222; .ASPXAUTH=6562F5FE1B07F48DEDFFD9B46064D4D549B58CAD1B40A275E42C4E76EB52DA0BAB939887B2FA316E7CD996FB2C0ABFFE541E66BF17E17D469549B61596ECD481CC05755C5963B530A4A45B46418612D50EB23D7147637384AD5348F1767789B8CB5119F077DD8861B902EB21B8684F18; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM5NTUyMjIxLCJJYXQiOjE1Mzk1MTYyMjEsIkp0aSI6IjMwMjMzMTU5NCJ9.KxgzfG0X7X_AzJNzYfmgc7udhsmyhJYb96hlBRlWGwY; SERVERID=ee7868b4571d060d67d262c9840127e4|1539517806|1539514721"
        }
        url = "https://www.cdzk.cn/historydata/collegeenrolldiff?collegeHistoryID="+str(id)+"&code=0001"
        try:
            res = self.session.get(url,headers=collegeenrolldiff_heads,timeout=35)
        except Exception as err:
            print("获取 html 失败")
            self.db_cursor.execute(collegeenrolldiff_bad_data_sql, (id, "网络接口异常", '1'))
            print(err)
        soup = BeautifulSoup(res.text, "html.parser")
        tables = soup.findAll('table')
        trs = tables[0].findAll('tr')
        ths = tables[0].findAll('th')
        high_list = []
        # 读取第一行年份数据
        high_list.append([(re.sub('[^0-9]', '', str(th))) for th in ths[1:-7]])
        # 读取年份对应值
        [high_list.append([re.sub('[^0-9]','',str(td)) for td in tr.findAll('td')]) for tr in trs[1:]]
        # 转换列表数据方向算法
        with_list = rotate_list(high_list)
        for data in with_list:
            data.append(str(id)),(data.append('000'),data.append('000')) if len(data)==7 else data
            try:
                self.db_cursor.execute(collegeenrolldiff_data_sql, tuple(data))
                self.db.commit()
                print('插入数据成功，数据:')
                print(data)
            except Exception as err:
                print("插入数据库出错")
                print("错误数据：")
                print(data)
                self.db.rollback()
                self.db_cursor.execute(collegeenrolldiff_bad_data_sql, (id,str(data),'0'))
                print(err)

if __name__ == '__main__':
    GetZK(1,"测试").manage()
