#-*- codeing = utf-8 -*-
#@Author: LiAng
#@Time: 2022/9/28 22:19
#@File: test_proxy.py
#@Software:PyCharm

import urllib.request

url = 'http://httpbin.org/get'

headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53',
}
request = urllib.request.Request(url=url, headers=headers)

from test_free_proxy.Proxy import FreePoxy

proxy_list = []
# 得到免费代理
proxy_list = FreePoxy(proxy_kind='https').get_freeProxy01(proxy_list)
print(proxy_list)

# 下面是之前测试用的
proxies = {'http': '120.220.220.95:8085'}
handler = urllib.request.ProxyHandler(proxies=proxies)
opener = urllib.request.build_opener(handler)
response = opener.open(request)

# response = urllib.request.urlopen(request)



content = response.read().decode('utf-8')
print(content)