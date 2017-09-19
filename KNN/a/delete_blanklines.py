 # -*- coding:utf-8 -*-
'''
 * 删除空白行
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
infp = open("a.txt", "r")#包含空白行文档
outfp = open("a_all", "w")#删除空白行后的文档
results=''
lines = infp.readlines()
for li in lines:
    if li.split():
        results+=li
outfp.write(results)
infp.close()
outfp.close()
