import requests as rq
import re
import pandas as pd
url='http://rate.tmall.com/list_detail_rate.htm?itemId=41464129793&sellerId=1652490016&currentPage=1'
myweb = rq.get(url)
myjson = re.findall('\"rateList\":(\[.*?\])\,\"tags\"',myweb.text)[0]
mytable = pd.read_json(myjson)
mytable.to_csv('mytable.txt')
mytable.to_excel('mytable.xls')
