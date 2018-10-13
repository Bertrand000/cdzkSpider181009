# -*- coding: utf-8 -*-
import requests
import http.cookiejar as cookielib
import configparser
import json
import jsonpath
import re
import pymysql
from bs4 import BeautifulSoup

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
        for id in id_list:
            # self.get_enrollDetail(id)
            # self.get_specialtyEnrollDiff(id)
            self.get_collegeenrolldiff(id)
        print("---------------------------------------------------------------------------------------------------------h")
        print("enroll 数据爬取完成")
    def get_specialtyEnrollDiff(self,id):
        specialtyEnrollDiff_base_data_sql = '''REPLACE INTO
                                          specialtyEnrollDiff_base(SpecialtyHistoryID,SpecialtyCode,SpeicaltyName,CollegeHistoryID,SpecComment)
                                          VALUES(%s,%s,%s,%s,%s)'''
        specialtyEnrollDiff_gradeDiffs_data_sql = '''REPLACE INTO
                                                  specialtyEnrollDiff_gradeDiffs(SpecialtyHistoryID,SpecialtyGradeDiffYear,MatricGrade,SpecialtyGradeDiff,AverageGrade,AverageGradeDiff,MatricGradePosition,AverageGradePosition)
                                                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
        specialtyEnrollDiff_bad_data_sql = '''REPLACE INTO
                                                  specialtyEnrollDiff_bad(bad_data_value)
                                                  VALUES(%s)'''
        specialtyEnrollDiff_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
            ,"origin":"https://www.cdzk.cn"
            ,"X-Requested-With": "XMLHttpRequest"
            ,"referer": "https://www.cdzk.cn/HistoryData/SpecialtyEnrollDiff"
            ,"cookie": "LoginName=13551031630; last_card=868916619; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMjNhMTZhZDMtOTY1Ny00ZDlmLTk5ZDMtZWVlOTA1NDEzNTM2IiwibmJmIjoxNTM4MDE4NzgxLCJleHAiOjE1NDA2MTA3ODEsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.PosZChb02jPEVhHLK21sIykyUybYTb9204rXm0pR95k; Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1538018073,1538210977,1538269879,1539305694; ASP.NET_SessionId=ceolwps0ufloa5jcfnytksh0; canRedir=no; __RequestVerificationToken=i5OldJsWuhkca7TXfhSvjSTFW3KQRI4yF_G8zn5kEIhRgIb5g6vee70giYIwyyKbd-CLN3ojnPj3wsr8E4KODwGguF055Z_rx3-UHEh3hgE1; .ASPXAUTH=1455849280EF85FED4C32D8F28A27610E5DF73F74832A79F0846FD38BFD7181E3D83289667CF6DA8F8A4B6C22529E9FF419412E0D2708220E096A19A54D9DCC04C67BB944234D4C1D5EC02C5BBE41FA44FBD4841B806A09815C6D169E2AD60BF9FCE9225F99D2E99B86B3780D7D8DDFD; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM5MzU2NTQ4LCJJYXQiOjE1MzkzMjA1NDgsIkp0aSI6IjE0MzkzNzM5NTMifQ.UXuog4AZQ1ZUK7us60-AZVfhumgCKFJRHbIlHL_zRFo; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1539320557; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1539320551|1539320546"
        }
        specialtyEnrollDiff_url = "https://www.cdzk.cn/HistoryData/GetSpecialtyEnrollDiff?collegeHistoryID=" + str(id) + "&pageSize=10000&currentPage=1"
        try:
            resp = self.session.post(specialtyEnrollDiff_url, headers=specialtyEnrollDiff_headers,timeout=35)
            self.session.cookies.save()
            unicodestr = json.loads(str(resp.text))
            data = jsonpath.jsonpath(unicodestr, "$.data")
            if not data[0]:
                print("data数据为空")
                self.db_cursor.execute(specialtyEnrollDiff_bad_data_sql,"空数据 id: " + str(id))
                self.db.commit()
                return None
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
                    self.db_cursor.execute(specialtyEnrollDiff_bad_data_sql,"错误数据 id: " + str(id) + "内容 获取到的数据:" + str(data))
                    print(err)
                for gradeDiffs_data in base_data['GradeDiffs']:
                    specialtyEnrollDiff_gradeDiffs_data = (gradeDiffs_data['SpecialtyHistoryID'],gradeDiffs_data['SpecialtyGradeDiffYear'],gradeDiffs_data['MatricGrade'],gradeDiffs_data['SpecialtyGradeDiff'],gradeDiffs_data['AverageGrade'],gradeDiffs_data['AverageGradeDiff'],gradeDiffs_data['MatricGradePosition'],gradeDiffs_data['AverageGradePosition'])
                    try:
                        print("获取到数据：")
                        print(base_data)
                        self.db_cursor.execute(specialtyEnrollDiff_gradeDiffs_data_sql, specialtyEnrollDiff_gradeDiffs_data)
                        self.db.commit()
                    except Exception as err:
                        print("插入数据库出错")
                        self.db.rollback()
                        self.db_cursor.execute(specialtyEnrollDiff_bad_data_sql, "错误数据内容: " + str(specialtyEnrollDiff_gradeDiffs_data))
                        print(err)
        except Exception as err:
            print("读取接口失败 数据id：" + str(id))
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
    def get_collegeenrolldiff(self,id):
        collegeenrolldiff_heads = {
            'authority':'www.cdzk.cn'
            ,'method':'GET'
            ,"scheme":"https"
            ,"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
            ,"accept-encoding":"gzip, deflate, br"
            ,"accept-language":"zh-CN,zh;q=0.9"
            ,'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
            ,"cookie": "ASP.NET_SessionId=5fgkdjorro1rlo1s2zbfavpx; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMDRlNmVjM2MtODVlNS00YTFhLTljZTktYjJkZTMwMWMxY2Y5IiwibmJmIjoxNTM4MTQzODk3LCJleHAiOjE1NDA3MzU4OTcsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.fU2WfMJXtjRCANebB6xWTBIdtywBsvfKZ0ejgejm3fY; __RequestVerificationToken=wuQr51hVLBonjGVTKDPcmUga5Hx67udr4It5E1utghKCdkWyXe4l2FRv0X2x1kXSBlg498jGn7QgHx4PVR_pXb-VGZQtKcO0710xGS_zryE1; Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1538143778; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1538238276; LoginName=13551031630; .ASPXAUTH=58998A48ABC89178205192365B5BB65C3D16BDBC9516D915EB7E0462B6BD5EC96082717508163A6660A8FB2F1AF548EC574E2F49621F9C260BCB03E670A43BA7540B33DEE7CCFA8B60418CA2C64FA6392AF61B5BA60E38756BF6C4C0EC1DA69260ACB290D2E2430B532F0FEF21F46045; last_card=868916619; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1538239474|1538236939"
            ,"referer":"https://www.cdzk.cn/historydata/collegeenrolldiff?collegeHistoryID=" + str(id) + "&code=0001"
            ,"upgrade-insecure-requests":"1"
        }
        url = "https://www.cdzk.cn/historydata/collegeenrolldiff?collegeHistoryID=" + str(id) + "&code=0001"
        res = self.session.get(url,heads=collegeenrolldiff_heads,timeout=35)
        Soup = BeautifulSoup(res.text, "lxml")
if __name__ == '__main__':
    GetZK(1,"测试").manage()
