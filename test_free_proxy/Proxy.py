
import time
import platform
import requests
#import ssl
import random
import urllib3
import os
import datetime
import hashlib
import json
import shutil
import wget
import re
import multiprocessing
import math
import argparse
import sys
from zhconv import convert
from pymysql import connect
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

# from func_timeout import func_set_timeout, FunctionTimedOut
from urllib.parse import urlparse, quote
#from magic_google import MagicGoogle
from pprint import pprint

def vi_error(type = "", tag = "", exception = "", valuelist = [], log_path = "./LOG"):
    try:
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        log_file = type + "." + tag + "." + str(os.getpid()) + "." + str(time.time()) + ".log"
        with open(os.path.join(log_path, log_file), "w", encoding = "utf-8") as f_log:                
            error = "\n".join([str(datetime.datetime.now()), str(os.getpid()), str(type), str(tag), str(exception)])
            print(error)     
            f_log.write(error + "\n")
            for v in valuelist:
                try:
                    if isinstance(v, str):
                        f_log.write(v + "\n")
                    else:
                        f_log.write(json.dumps(v) + "\n")
                except Exception as e:
                    print(str(e))
                    f_log.write(str(v) + "\n")
    except Exception as e:
        print("vi_error: " + str(e))
        time.sleep(60)
    return None

def prepare_terminate_file(terminate_file):
    if terminate_file != "":
        try:
            if os.path.exists(terminate_file + ".ok"):
                info = "prepare_terminate_file: " + "rename path: " + terminate_file
                os.rename(terminate_file + ".ok", terminate_file + ".ing")
            if not os.path.exists(terminate_file + ".ing"):
                info = "prepare_terminate_file: " + "create terminate_file: " + terminate_file + ".ing"
                os.mkdir(terminate_file + ".ing")
            else:
                info = "prepare_terminate_file: " + "create terminate_file: " + terminate_file + ".ing"
            #print(info)
        except Exception as e:
            print("prepare_terminate_file: " + str(os.getpid()) + ": " + "error prepare_terminate_file: " + str(e))
            terminate_file = ""
    return terminate_file

class FreePoxy:
    def get_pay_kuaidaili(self, proxy_list, max_retry_time = 2):
        process_start = time.time()        
        retry_time = 0
        while retry_time < max_retry_time:
            try:                
                res = requests.get(self.kuaidaili_url, headers = self.header, timeout = self.timeout)
                if res.status_code == 200:
                    if self.kuaidaili_url.find("vip") == -1:
                        results = res.text.split("\n")
                    else:
                        results = (res.json())["data"]["proxy_list"]                    
                    print("FreePoxy: " + str(os.getpid()) + ": get_pay_kuaidaili: " + str(len(results)))
                    retry_time = max_retry_time                   
                    for ip in results:                            
                        if ip not in proxy_list:
                            #print(ip)
                            proxy_list[ip] = {"IP":ip, "From":self.kuaidaili_url}                    
                else:
                    print("FreePoxy: " + str(os.getpid()) + ": " + "error kuaidaili status " + self.kuaidaili_url)
            except Exception as e:
                print("FreePoxy: " + str(os.getpid()) + ": " + "error kuaidaili connect " + self.kuaidaili_url + ": " + str(e))
            retry_time = retry_time + 1
            time.sleep(3)
        print("FreePoxy: " + str(os.getpid()) + ": " + "get pay proxy time used: " + str(time.time() - process_start))
        return proxy_list
        
    def get_pay_xiguadaili(self, proxy_list, max_retry_time = 2):
        process_start = time.time()        
        retry_time = 0
        while retry_time < max_retry_time:
            try:                
                res = requests.get(self.xiguadaili_url, headers = self.header, timeout = self.timeout)                
                if res.status_code == 200:
                    results = res.json()
                    if "error" not in results and len(results) > 0:
                        print("FreePoxy: " + str(os.getpid()) + ": " + "get_pay_xiguadaili: " + str(len(results)))
                        retry_time = max_retry_time                   
                        for ip in results:
                            ip = ip["host"] + ":" + str(ip["port"])
                            if ip not in proxy_list.keys():
                                #print(ip)
                                proxy_list[ip] = {"IP":ip, "From":self.xiguadaili_url}
                    else:
                        print("FreePoxy: " + str(os.getpid()) + ": " + "error xiguadaili response")
                else:
                    print("FreePoxy: " + str(os.getpid()) + ": " + "error xiguadaili status")
            except:
                print("FreePoxy: " + str(os.getpid()) + ": " + "error xiguadaili connect")
            retry_time = retry_time + 1
            time.sleep(3)
        print("FreePoxy: " + str(os.getpid()) + ": " + "get pay proxy time used: " + str(time.time() - process_start))
        return proxy_list

    def get_freeProxy01(self, proxy_list):
        process_start = time.time()        
        for url in self.freeproxy_urls:
            if self.terminate_file != "" and os.path.exists(self.terminate_file + ".ok"):
                return proxy_list
            #print(url)
            try:
                res = requests.get(url, headers = self.header, timeout = self.timeout)                
                if res.status_code == 200:
                    p = re.compile(r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)[\s\S]+?([0-9]+)')
                    chall = re.findall(p, res.text)
                    print("FreePoxy: " + str(os.getpid()) + ": " + url + ": " + str(len(chall)))
                    #print(chall)
                    for ip in chall:
                        ip = ip[0] + ":" + ip[1]
                        if ip not in proxy_list.keys():
                            #print(ip)
                            proxy_list[ip] = {"IP":ip, "From":url}
                else:
                    print("FreePoxy: " + str(os.getpid()) + ": " + self.proxy_kind + ": status error proxy web site: " + url)
            except:
                print("FreePoxy: " + str(os.getpid()) + ": " + self.proxy_kind + ": connect error proxy web site: " + url)
        print("FreePoxy: " + str(os.getpid()) + ": " + "get freeProxy01 time used: " + str(time.time() - process_start))

        return proxy_list
    
    def update_proxy(self, proxy_list):
        process_start = time.time()
        try:
            db = connect(host = self.host, user = self.user, password = self.password, database = self.database)
            db.autocommit(True)
            cursor = db.cursor()
            for proxy in proxy_list:
                if self.terminate_file != "" and os.path.exists(self.terminate_file + ".ok"):
                    return True
                p_list = []
                if "://" in proxy["IP"]:
                    p_list.append({'http': proxy["IP"], 'https': proxy["IP"], "ftp": proxy["IP"]})
                    p_list.append({'http': "socks5://" + proxy["IP"], 'https': "socks5://" + proxy["IP"], "ftp": "socks5://" + proxy["IP"]})
                else:
                    p_list.append({'http': "http://" + proxy["IP"], 'https': "https://" + proxy["IP"], "ftp": "ftp://" + proxy["IP"]})
                try:
                    for p in p_list:
                        res = requests.get(url = self.test_urls[self.proxy_kind], headers = self.header, timeout = self.timeout, proxies = p)
                        if res.status_code == 200:
                            print("FreePoxy: " + str(os.getpid()) + ": " + "proxy find: " + proxy["IP"] + " for " + self.test_urls[self.proxy_kind])
                            sql_result = cursor.execute("select `IP` from `" + self.proxy_kind + "` where `IP`='" + proxy["IP"] + "'")
                            if sql_result == 0:
                                cursor.execute('insert into `' + self.proxy_kind + '` (`IP`, `status`, `From`, `LastChecked`) VALUES ("' + proxy["IP"] + '", "' + 'Yes' + '", "' + proxy["From"] + '", "' + str(datetime.datetime.now()) + '")')
                            else:
                                cursor.execute("update `" + self.proxy_kind + "` set `status`='Yes', `From`='" + proxy["From"] + "' , `LastChecked`='" + str(datetime.datetime.now()) + "' where `IP`='" + proxy["IP"] + "'")
                            continue
                        else:
                            error = "FreePoxy: " + str(os.getpid()) + ": " + "status error: " + self.test_urls[self.proxy_kind] + str(p)
                except Exception as e:
                    error = "FreePoxy: " + str(os.getpid()) + ": " + "connect error: " + self.test_urls[self.proxy_kind] + str(p) + ": " + str(e)
                #print(error)
                cursor.execute("delete from `" + self.proxy_kind  + "` WHERE `IP`='" + proxy["IP"] + "'")
            db.close()
        except Exception as e:
            vi_error(type="FreePoxy",tag="update_proxy",exception=str(e),valuelist=[])
            return False
        print("FreePoxy: " + str(os.getpid()) + ": " + "update proxy time used: " + str(time.time() - process_start))
        return True

    def multi_update_proxy(self):
        process_start = time.time()
        try:            
            db = connect(host = self.host, user = self.user, password = self.password)
            db.autocommit(True)
            cursor = db.cursor()
            sql_result = cursor.execute("SELECT * FROM information_schema.SCHEMATA where SCHEMA_NAME='" + self.database + "'")
            if sql_result == 0:
                cursor.execute("create database `" + self.database + "` default character set utf8mb4")
            sql_result = cursor.execute("select TABLE_NAME from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA='" + self.database + "' and TABLE_NAME='" + self.proxy_kind + "'")        
            if sql_result == 0:
                cursor.execute("create table if not exists `" + self.database + "`.`" + self.proxy_kind + "` (`IP` CHAR(30), `status` ENUM('Yes','No'), `From` CHAR(250), `LastChecked` CHAR(250))")            
        except Exception as e:
            print("FreePoxy: error: " + str(e))    
            return False        
        while self.terminate_file == "" or (self.terminate_file != "" and not os.path.exists(self.terminate_file + ".ok")):
            try:
                proxy_list = {}
                for proxy in self.pre_proxy_list:
                    ip = {"IP": proxy, "From": "pre_proxy"}
                    if ip["IP"] not in proxy_list:
                        proxy_list[ip["IP"]] = ip
                cursor.execute("select `IP`, `From` from `" + self.database + "`.`" + self.proxy_kind + "`")
                for proxy in cursor.fetchall():
                    ip = {"IP": proxy[0], "From": proxy[1]}
                    if ip["IP"] not in proxy_list:
                        proxy_list[ip["IP"]] = ip
                print("FreePoxy: " + str(os.getpid()) + ": " + "mysql and pre_proxy own all possible proxy: " + self.proxy_kind + ": " + str(len(proxy_list)))
                if self.use_xiguadaili_tid != "":
                    proxy_list = self.get_pay_xiguadaili(proxy_list)
                if self.use_kuaidaili_tid != "":
                    proxy_list = self.get_pay_kuaidaili(proxy_list)                    
                if self.is_use_free == True:
                    proxy_list = self.get_freeProxy01(proxy_list)
                proxy_list = list(proxy_list.values())
                random.shuffle(proxy_list)
                print("FreePoxy: " + str(os.getpid()) + ": " + "all possible proxy: " + self.proxy_kind + ": " + str(len(proxy_list)))
                if len(proxy_list) > 0:
                    if self.process_num == 1:
                        self.update_proxy(proxy_list)
                    else:
                        n = math.ceil(len(proxy_list)/self.process_num)
                        with multiprocessing.Pool(self.process_num) as p:
                            p.map(self.update_proxy, [proxy_list[i:i+n] for i in range(0, len(proxy_list), n)])
                    print("FreePoxy: " + str(os.getpid()) + ": " + "update proxy time used: " + str(time.time() - process_start) + " and now is sleeping: " + str(datetime.datetime.now()))
                if self.is_use_free == True:
                    time.sleep(self.freeproxy_sleep_time)
            except Exception as e:
                vi_error(type="FreePoxy",tag="multi_update_proxy",exception=str(e),valuelist=[])
        db.close()
        print("FreePoxy: " + str(os.getpid()) + ": " + "all time used: " + str(time.time() - process_start))
        return True
        
    def __init__(self, proxy_kind, terminate_file = "", process_num = 1, use_kuaidaili_tid = "", pre_proxy_list = ["127.0.0.1:1080"]): #pre_proxy_list = ["socks5h://127.0.0.1:8080"]
        self.terminate_file = prepare_terminate_file(terminate_file)
        self.proxy_kind = proxy_kind
        self.process_num = process_num
        self.is_use_free = False if use_kuaidaili_tid else True
        self.pre_proxy_list = ["socks5h://" + host for host in pre_proxy_list]

        self.test_urls = {"alexa": "http://data.alexa.com/data?cli=10&url=baidu.com",
                          "fofa": "https://fofa.so/",
                          "google": 'https://www.google.com/',
                          "censys": 'https://censys.io/',
                          "0day": 'https://0day.today/',
                          "ipinfo": 'https://ipinfo.io/AS6',
                         }

        self.freeproxy_sleep_time = 60*0
        self.timeout = (15,30)
        
        self.use_xiguadaili_tid = ""   
        self.xiguadaili_url = "http://api3.xiguadaili.com/ip/?tid=" + self.use_xiguadaili_tid + "&num=20&longlife=20&format=json"        
        self.use_kuaidaili_tid = use_kuaidaili_tid     
        self.kuaidaili_url = "https://dev.kdlapi.com/api/getproxy/?orderid="+use_kuaidaili_tid+"&num=100&protocol=2&method=2&sep=2"
        self.use_vip_kuaidaili_tid = ""
        self.kuaidaili_url_vip = "https://svip.kdlapi.com/api/getproxy/?orderid="+use_kuaidaili_tid+"&num=30&protocol=2&method=2&quality=2&format=json"

        self.host = "localhost"
        self.user = "root"
        self.password = "toor"
        self.database = "freeproxy"
        
        self.freeproxy_urls = [
                        "https://free-proxy-list.net/",
                        "https://www.sslproxies.org/", 
                        "https://www.us-proxy.org/", 
                        "https://www.socks-proxy.net/",
                        "http://www.66ip.cn/", 
                        "http://www.cz88.net/proxy/",
                        "http://www.iphai.com/free/ng",
                        "http://www.iphai.com/free/np",
                        "http://www.iphai.com/free/wg",
                        "http://www.iphai.com/free/wp",] + \
                        ["https://www.xicidaili.com/nn/" + str(i+1) for i in range(3)] + \
                        ["https://www.xicidaili.com/nt/" + str(i+1) for i in range(3)] + \
                        ["https://www.xicidaili.com/wn/" + str(i+1) for i in range(3)] + \
                        ["https://www.xicidaili.com/wt/" + str(i+1) for i in range(3)] + \
                        ["https://www.kuaidaili.com/free/inha/" + str(i+1) + "/" for i in range(1)] + \
                        ["https://www.kuaidaili.com/free/intr/" + str(i+1) + "/" for i in range(1)] + \
                        ["http://www.66ip.cn/areaindex_" + str(i+1) + "/1.html" for i in range(34)] + \
                        ["http://www.89ip.cn/index_" + str(i+1) + ".html" for i in range(3)] + \
                        ["http://www.hailiangip.com/freeAgency/1?page=" + str(i+1) for i in range(1)] + \
                        ["http://www.hailiangip.com/freeAgency/2?page=" + str(i+1) for i in range(1)]

        self.header = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                       "Accept-Language": "zh-CN,zh;q=0.9",
                       "Cache-Control": "max-age=0",
                       "Accept-Encoding": "gzip, deflate",
                       "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
                      }
