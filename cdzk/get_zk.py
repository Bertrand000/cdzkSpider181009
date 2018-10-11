# -*- coding: utf-8 -*-
import requests
import http.cookiejar as cookielib
import configparser
import json
import jsonpath
import re
import pymysql
from cdzk.dao.model.cdzk_basedata_model import *
from cdzk.dao.DB_service import *

# 获取配置
cfg = configparser.ConfigParser()
cfg.read("config.ini")

class GetZK():
    session = None
    config = None
    def __init__(self, threadID=1, name=''):
        # 创建实体类
        self.data = Cdzk()
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

    # # json处理
    # def json_data(self):
    #     bad_data_sql = '''REPLACE INTO
    #                                                       base_data(collegeHistoryId,gradeDiffLevel,order_1,subject_1,collegeCode,collegeName,province)
    #                                                       VALUES(%s,%s,%s,%s,%s,%s,%s)'''
    #     base_data_object = open("json_data.txt", "r", encoding='utf-8')
    #     try:
    #         data_context = base_data_object.read()
    #     finally:
    #         base_data_object.close()
    #     data_context = re.sub('\'', '\"', data_context)
    #     unicodestr = json.loads(str(data_context))
    #     json_list = jsonpath.jsonpath(unicodestr, "$.data.items")
    #     for data in json_list[0]:
    #         try:
    #             print("获取到数据：")
    #             self.db_cursor.execute(bad_data_sql, tuple(data.values()))
    #             self.db.commit()
    #         except Exception as err:
    #             print("插入数据库出错")
    #             print("获取到数据：")
    #             self.db.rollback()
    #             print(err)
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
            self.get_specialtyEnrollDiff(id)
        print("---------------------------------------------------------------------------------------------------------")
        print("数据爬取完成")
    def get_specialtyEnrollDiff(self,id):
        save_sprcialty_base_data_sql = '''REPLACE INTO
                                          sprcialty_base_data(SpecialtyHistoryID,SpecialtyCode,SpeicaltyName,CollegeHistoryID,SpecComment)
                                          VALUES(%s,%s,%s,%s,%s)'''

        save_sprcialty_gradeDiffs_data_sql = '''REPLACE INTO
                                          sprcialty_gradediffs_data(SpecialtyHistoryID,SpecialtyGradeDiffYear,MatricGrade,SpecialtyGradeDiff,AverageGrade,AverageGradeDiff,MatricGradePosition,AverageGradePosition)
                                          VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
        bad_data_sql = '''REPLACE INTO
                                          sprcialty_bad_data(bad_value)
                                          VALUES(%s)'''
        specialtyEnrollDiff_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
            , "origin": "https://www.cdzk.cn"
            , "X-Requested-With": "XMLHttpRequest"
            , "referer": "https://www.cdzk.cn/HistoryData/SpecialtyEnrollDiff"
            , "cookie": "Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1539182695,1539263368; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1539274372; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiOGFiYTY4ODgtYTE1YS00M2JmLTgxZDUtZGU4YjQ0YmU1MjM0IiwibmJmIjoxNTM5MTgyNzEyLCJleHAiOjE1NDE3NzQ3MTIsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.LE9H3KL6JGH-4YzlCpJz9dIKlp5vt4bv5LlSl-jQRyQ; LoginName=13551031630; last_card=868916619; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1539274372|1539271924; ASP.NET_SessionId=plgksne4vs2i4cjztxnufwph; __RequestVerificationToken=yTw6vqcwT6toWW6Sh-K4Mi1ZUJPWhwdUq8CsbiJ4s-OkOi1fDkTusWmgHGNEau5jdrAWHMqqBla2suObdAwSPf0P5byfWAETwPbNsZbo_v41; .ASPXAUTH=83F974A6A4BA0E2B7A156B947841D86C0F2CBF0B031BA2CE90BB24FC3006DE0153528A017ECCC965F079A9D9E7857C1D6EF332DCB78E3544316B04657808DBD4AA9D3507D764E5199ADDFFE0AB6115D8DA0C5E64DF7945702CA9615C143A72FC6F93CC27225670AB96248B33C4C46B31; canRedir=no; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM5MzEwMzY3LCJJYXQiOjE1MzkyNzQzNjcsIkp0aSI6IjE3NDY0OTcyNDcifQ.0p72XDJk_W95x3tZyUUdr6csRD4dfJt94gCJlz3YSCI"
        }
        specialtyEnrollDiff_url = "https://www.cdzk.cn/HistoryData/GetSpecialtyEnrollDiff?collegeHistoryID=" + str(id) + "&pageSize=10000&currentPage=1"
        resp = self.session.post(specialtyEnrollDiff_url, headers=specialtyEnrollDiff_headers, timeout=35)
        unicodestr = json.loads(str(resp.text))
        str_data = unicodestr['data']
        if not str_data:
            print(str(id) + "无数据")
            try:
                self.db_cursor.execute(bad_data_sql, 'id:' + str(id) + "无数据")
                self.db.commit()
            except Exception as err:
                self.db.rollback()
                print(err)
            return None
        list_data = json.loads(str_data)
        for data in list_data:
            try:
                sprcialty_base_data = (data['SpecialtyHistoryID'],data['SpecialtyCode'],data['SpeicaltyName'],data['CollegeHistoryID'],data['SpecComment'])
                print("获取到数据：")
                print(data)
                self.db_cursor.execute(save_sprcialty_base_data_sql, sprcialty_base_data)
                self.db.commit()
            except Exception as err:
                print("插入数据库出错,错误数据：")
                print(data)
                print("---------------------------------------------------------------")
                self.db.rollback()
                self.db_cursor.execute(bad_data_sql, (str(data)))
                print(err)
            for gradeDiffs in data['GradeDiffs']:
                try:
                    sprcialty_gradeDiffs_data = (gradeDiffs['SpecialtyHistoryID'],gradeDiffs['SpecialtyGradeDiffYear'],gradeDiffs['MatricGrade'],gradeDiffs['SpecialtyGradeDiff'],gradeDiffs['AverageGrade'],gradeDiffs['AverageGradeDiff'],gradeDiffs['MatricGradePosition'],gradeDiffs['AverageGradePosition'])
                    print("获取到数据：")
                    print(gradeDiffs)
                    self.db_cursor.execute(save_sprcialty_gradeDiffs_data_sql, sprcialty_gradeDiffs_data)
                    self.db.commit()
                except Exception as err:
                    print("插入数据库子数据出错,错误父数据：")
                    print(data)
                    print("子数据：")
                    print(gradeDiffs)
                    print("---------------------------------------------------------------")
                    self.db.rollback()
                    self.db_cursor.execute(bad_data_sql, (str(gradeDiffs)))
                    print(err)

    def get_enrollDetail(self, id):

        enrollDetail_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
            , "authority": "m.in985.com"
            , "method": "GET"
            , "path": "/api/v1/history/college/enrollDetail/47"
            , "scheme": "https"
            , "accept": "application/json, text/javascript, */*; q=0.01"
            , "accept-encoding": "gzip, deflate, br"
            , "accept-language": "zh-CN,zh;q=0.8"
            , "authorization": "eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU"
            , "origin": "https://www.cdzk.cn"
            , "referer": "https://www.cdzk.cn/historydata/collegeenrolldetail?collegeHistoryID=" + str(id) + "&code=0"
            , "cookie": "ASP.NET_SessionId=5fgkdjorro1rlo1s2zbfavpx; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMDRlNmVjM2MtODVlNS00YTFhLTljZTktYjJkZTMwMWMxY2Y5IiwibmJmIjoxNTM4MTQzODk3LCJleHAiOjE1NDA3MzU4OTcsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.fU2WfMJXtjRCANebB6xWTBIdtywBsvfKZ0ejgejm3fY; __RequestVerificationToken=wuQr51hVLBonjGVTKDPcmUga5Hx67udr4It5E1utghKCdkWyXe4l2FRv0X2x1kXSBlg498jGn7QgHx4PVR_pXb-VGZQtKcO0710xGS_zryE1; Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1538143778; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1538238276; LoginName=13551031630; .ASPXAUTH=58998A48ABC89178205192365B5BB65C3D16BDBC9516D915EB7E0462B6BD5EC96082717508163A6660A8FB2F1AF548EC574E2F49621F9C260BCB03E670A43BA7540B33DEE7CCFA8B60418CA2C64FA6392AF61B5BA60E38756BF6C4C0EC1DA69260ACB290D2E2430B532F0FEF21F46045; last_card=868916619; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1538239474|1538236939"
        }
        enrollDetail_url = "https://m.in985.com/api/v1/history/college/enrollDetail/" + str(id)
        bad_data_sql = '''REPLACE INTO
                                                  bad_data(nodata_source_id)
                                                  VALUES(%s)'''
        replace_sql = '''REPLACE INTO
                                          enroll_detail(source_id,year,real_recruit_total,first_wish_total,enroll_property,first_wish_suc_total,second_wish_suc_total)
                                          VALUES(%s,%s,%s,%s,%s,%s,%s)'''
        try:
            resp = self.session.get(enrollDetail_url, headers=enrollDetail_headers,timeout=35)
            unicodestr = json.loads(str(resp.text))
            data_list = jsonpath.jsonpath(unicodestr, "$.data.*")
            if not data_list:
                print("id:"+ str(id) + "无数据")
                try:
                    print("获取到数据：")
                    self.db_cursor.execute(bad_data_sql, id)
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
    # 获取高校录取详情and专业录取分数  JSON  高校录取详情 if self.ope = 1 else 专业录取分数
    def get_enrollDetail_specialtyEnrollDiff(self,id,ope=1):
        if not id:
            print("id 或者code 不能为空")
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
            ,"authorization": "eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU"
            , "origin": "https://www.cdzk.cn"
            , "referer": "https://www.cdzk.cn/historydata/collegeenrolldetail?collegeHistoryID="+ str(id) +"&code=0"
            ,"cookie": "ASP.NET_SessionId=5fgkdjorro1rlo1s2zbfavpx; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMDRlNmVjM2MtODVlNS00YTFhLTljZTktYjJkZTMwMWMxY2Y5IiwibmJmIjoxNTM4MTQzODk3LCJleHAiOjE1NDA3MzU4OTcsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.fU2WfMJXtjRCANebB6xWTBIdtywBsvfKZ0ejgejm3fY; __RequestVerificationToken=wuQr51hVLBonjGVTKDPcmUga5Hx67udr4It5E1utghKCdkWyXe4l2FRv0X2x1kXSBlg498jGn7QgHx4PVR_pXb-VGZQtKcO0710xGS_zryE1; Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1538143778; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1538238276; LoginName=13551031630; .ASPXAUTH=58998A48ABC89178205192365B5BB65C3D16BDBC9516D915EB7E0462B6BD5EC96082717508163A6660A8FB2F1AF548EC574E2F49621F9C260BCB03E670A43BA7540B33DEE7CCFA8B60418CA2C64FA6392AF61B5BA60E38756BF6C4C0EC1DA69260ACB290D2E2430B532F0FEF21F46045; last_card=868916619; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1538239474|1538236939"
        }
        specialtyEnrollDiff_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
            # ,"authority":"www.cdzk.cn"
            # ,"method":"POST"
            # ,"path":"/HistoryData/GetSpecialtyEnrollDiff"
            # ,"scheme":"https"
            # ,"accept":"application/json, text/javascript, */*; q=0.01"
            # ,"accept-encoding":"gzip, deflate, br"
            # ,"accept-language":"zh-CN,zh;q=0.8"
            # ,"content-length":"45"
            # ,"content-type":"application/x-www-form-urlencoded; charset=UTF-8"
            ,"origin":"https://www.cdzk.cn"
            ,"X-Requested-With": "XMLHttpRequest"
            ,"referer": "https://www.cdzk.cn/HistoryData/SpecialtyEnrollDiff"
            ,"cookie": "ASP.NET_SessionId=5fgkdjorro1rlo1s2zbfavpx; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMDRlNmVjM2MtODVlNS00YTFhLTljZTktYjJkZTMwMWMxY2Y5IiwibmJmIjoxNTM4MTQzODk3LCJleHAiOjE1NDA3MzU4OTcsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.fU2WfMJXtjRCANebB6xWTBIdtywBsvfKZ0ejgejm3fY; __RequestVerificationToken=wuQr51hVLBonjGVTKDPcmUga5Hx67udr4It5E1utghKCdkWyXe4l2FRv0X2x1kXSBlg498jGn7QgHx4PVR_pXb-VGZQtKcO0710xGS_zryE1; Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1538143778; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1538238276; LoginName=13551031630; .ASPXAUTH=58998A48ABC89178205192365B5BB65C3D16BDBC9516D915EB7E0462B6BD5EC96082717508163A6660A8FB2F1AF548EC574E2F49621F9C260BCB03E670A43BA7540B33DEE7CCFA8B60418CA2C64FA6392AF61B5BA60E38756BF6C4C0EC1DA69260ACB290D2E2430B532F0FEF21F46045; last_card=868916619; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1538239474|1538236939"
        }
        enrollDetail_url = "https://m.in985.com/api/v1/history/college/enrollDetail/" + str(id)
        specialtyEnrollDiff_url = "https://www.cdzk.cn/HistoryData/GetSpecialtyEnrollDiff?collegeHistoryID=" + str(id) + "&pageSize=10000&currentPage=1"
        try:
            resp = self.session.get(enrollDetail_url, headers=enrollDetail_headers, timeout=35) if ope==1 else self.session.post(specialtyEnrollDiff_url, headers=specialtyEnrollDiff_headers ,timeout=35)
            unicodestr = json.loads(str(resp.text))
            # txt_object = open("enrollDetail_json.txt" if ope == 1 else "specialtyEnrollDiff_json.txt","a",encoding="utf-8")
            # try:
            #     txt_object.write("\n"+str(unicodestr))
            # except Exception as err:
            #     print("写入失败")
            #     print(err)
            #     return None
            # finally:
            #     txt_object.close()
        except Exception as err:
            print("获取接口数据失败")
            print("url:"+enrollDetail_url if ope == 1 else specialtyEnrollDiff_url +"\n------------------"+err)
            return None
        print("写入成功\n写入数据:" + str(unicodestr))
    # def get_enrollDetail(self):
    #     if not id:
    #         print("id 或者code 不能为空")
    #         return None
    #     enrollDetail_headers = {
    #         "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
    #         ,"authority":"m.in985.com"
    #         , "method": "GET"
    #         ,"path":"/api/v1/history/college/enrollDetail/47"
    #         ,"scheme":"https"
    #         ,"accept":"application/json, text/javascript, */*; q=0.01"
    #         ,"accept-encoding":"gzip, deflate, br"
    #         ,"accept-language":"zh-CN,zh;q=0.8"
    #         ,"authorization":"eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU"
    #         ,"origin":"https://www.cdzk.cn"
    #         ,"referer": "https://www.cdzk.cn/historydata/collegeenrolldetail?collegeHistoryID=47&code=0"
    #         ,"cookie": "ASP.NET_SessionId=5fgkdjorro1rlo1s2zbfavpx; liveToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6MTE1NzgsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvdXNlcmRhdGEiOjIyOTQ3LCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9tb2JpbGVwaG9uZSI6IjEzNTUxMDMxNjMwIiwianRpIjoiMDRlNmVjM2MtODVlNS00YTFhLTljZTktYjJkZTMwMWMxY2Y5IiwibmJmIjoxNTM4MTQzODk3LCJleHAiOjE1NDA3MzU4OTcsImlzcyI6Ik1pbmd4IiwiYXVkIjoiTWluZ3gifQ.fU2WfMJXtjRCANebB6xWTBIdtywBsvfKZ0ejgejm3fY; __RequestVerificationToken=wuQr51hVLBonjGVTKDPcmUga5Hx67udr4It5E1utghKCdkWyXe4l2FRv0X2x1kXSBlg498jGn7QgHx4PVR_pXb-VGZQtKcO0710xGS_zryE1; Hm_lvt_eda497c7b8a0d42094679b6ed493be72=1538143778; Hm_lpvt_eda497c7b8a0d42094679b6ed493be72=1538238276; LoginName=13551031630; .ASPXAUTH=58998A48ABC89178205192365B5BB65C3D16BDBC9516D915EB7E0462B6BD5EC96082717508163A6660A8FB2F1AF548EC574E2F49621F9C260BCB03E670A43BA7540B33DEE7CCFA8B60418CA2C64FA6392AF61B5BA60E38756BF6C4C0EC1DA69260ACB290D2E2430B532F0FEF21F46045; last_card=868916619; PcRoadToken=eyJBbGciOiJSUzI1NiIsIlR5cCI6IkpXVCJ9.eyJJc3MiOm51bGwsIlN1YiI6IjEzNTUxMDMxNjMwOjg2ODkxNjYxOToyMjk0NyIsIkF1ZCI6Ik1pbmd4IiwiRXhwIjoxNTM4Mjc0MzA4LCJJYXQiOjE1MzgyMzgzMDgsIkp0aSI6IjEzNjE0NTQ2MzIifQ.90Hir_HsEqjueYRmqVSodkpgxUs0IimpJN82ZJpdGTU; SERVERID=1a306648965cfefa67e52a1a1b4180d4|1538239474|1538236939"
    #     }
    #     specialtyEnrollDiff_url = "https://m.in985.com/api/v1/history/college/enrollDetail/47"
    #     try:
    #         # resp = requests.post(specialtyEnrollDiff_url, headers=headers ,timeout=35)
    #         resp = self.session.get(specialtyEnrollDiff_url, headers=enrollDetail_headers, timeout=35)
    #         unicodestr = json.loads(str(resp.text))
    #     except Exception as err:
    #         print("获取接口数据失败")
    #         print("\n----------------------\nurl:"+specialtyEnrollDiff_url+"\n----------------------\n"+err)
    #         return None
    #     print("写入成功\n写入数据:" + str(unicodestr))




    # 获取高校录取分数方法 HTML解析
    # def get_collegeenrolldiff(self):


    # 处理需求数据，持久化数据
    def get_index_page_user(self):
        replace_sql = '''REPLACE INTO
                                  school_base_data(school_name,province,type,recruit_students_order,source_id)
                                  VALUES(%s,%s,%s,%s,%s)'''
        # index_html = self.get_index_page().replace("\n", "").replace("\r", "")
        index_data = self.get_enrollDetail_specialtyEnrollDiff(47)
        if not index_data:
            return
        # BS = BeautifulSoup(index_data, "html.parser")
        # tbody = BS.tbody
        # trs = tbody.contents
        # 去除 beautifulSoup 生产的空格子节点
        unicodestr = json.loads(str(index_data.text))
        # python形式的列表
        data_list = jsonpath.jsonpath(unicodestr,"$.data.items.*")
        for data in data_list:
            replace_data = []
            print(data)
            # try:
            #         print("获取到数据：")
            #         print(data)
            #         self.db_cursor.execute(replace_sql, replace_data)
            #         self.db.commit()
            #     except Exception as err:
            #         print("插入数据库出错")
            #         print("获取到数据：")
            #         print(replace_data)
            #         print("插入语句：" + self.db_cursor._last_executed)
            #         self.db.rollback()
            #         print(err)
            #         traceback.print_exc()
        # for tr in trs:
        #     replace_data = []
        #     if tr:
        #         contexts = tr.contents
        #         # 去除 beautifulSoup 生产的空格子节点
        #         while ' ' in contexts:
        #             contexts.remove(' ')
        #         for context in contexts:
        #             strContext = str(context)
        #             # 添加一组数据到列表中
        #             replace_data.append(strContext[strContext.find("(") + 2:strContext.find(")") - 1].split("'")[0]) if strContext.find("showlg") != -1 else replace_data.append(strContext[strContext.find(">")+1:strContext.rfind("<")])
        #         # 数据持久操作
        #         try:
        #             print("获取到数据：")
        #             print(replace_data)
        #             self.db_cursor.execute(replace_sql, replace_data)
        #             self.db.commit()
        #         except Exception as err:
        #             print("插入数据库出错")
        #             print("获取到数据：")
        #             print(replace_data)
        #             print("插入语句：" + self.db_cursor._last_executed)
        #             self.db.rollback()
        #             print(err)
        #             traceback.print_exc()
        #     else:
        #         print("获取高校基础数据失败")
        #         continue

if __name__ == '__main__':
    GetZK(1,"测试").manage()
