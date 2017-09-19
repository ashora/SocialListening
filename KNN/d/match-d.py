# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
f=open("t_with_cipin_d.txt","r") #读取文本
source=f.read().decode("utf-8")
#source="((ha()ha))"
#d=dict(source)

result=""

regStr="//(([^)]*)//)"# 正则表达式//(([^)]*)//)  ,([^)]*)，表示我要抽取的第一个左括号  其中[^)]*表示从左括号开始算起，直至遇到右括号之前的所有字符，然后还加上了分组符号()，是为了把括号里的字符定义为一个组，方便后面的抽取
pattern = re.compile(regStr)
results = pattern.findall(source)#找到中文,存储在results中
#source=source.replaceAll("(","").replaceAll(")","")
#source=source.replaceAll("(\\(\\))","")
#results= re.sub("[^h]", "", source) #替换所有匹配的子串用newstring替换subject中所有与正则表达式regex匹配的子串
#搜索文本中的中文字符，没搜索完一个中文词组隔一行输出。
results= re.sub(u"[^\u4e00-\u9fa5]{1,10}", "\n", source)#"\n"选择完中文字符后隔一行，输出下一行中文。u"[^\u4e00-\u9fa5]{1,10}"是中文编码范围
#for result in results :
print results
#print results.replace("\n"," ")
f=f=open("d.txt","w")  #将动词保存到另一个文档中
f.write(results)#.encode(encoding='utf-8')

