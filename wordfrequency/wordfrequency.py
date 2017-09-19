   # -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import nltk
f=open("t_with_POS_tag1.txt","r") #读取文本
sent=unicode(f.read().decode("utf-8"))
sTuple=[nltk.tag.str2tuple(t) for t in sent.split()]  #根据文本中的空格进行切分，切分后每一项再转为tuple元组，结构为: ('消息', 'N')
wordsCount=len(sTuple)  #统计词个数
print('words_sum:',wordsCount)
plt=nltk.FreqDist(sTuple) #获取统计结果，结果的结构为：<FreqDist: ('，', 'W'): 5, ('币', 'G'): 3,....>  每一项后面的数字是该字与其词性组合的出现次数，除了第一项的FreqDist外，后面的结构正好符合字典类型
print('各词性标注统计结果:')
d=dict(plt)  #把统计结果转为字典型，它会删掉不符合字典结构的第一项FreqDist，把后面的结果转存为字典型
dit=sorted(d.iteritems(),key=lambda asd:asd[1],reverse=True)
dt=dict(dit)
result=""
classify_n=""
classify_a=""
classify_an=""
classify_ag=""
classify_al=""
classify_ad=""
classify_v=""
#d.keys():  #遍历字典，每一类词性的总次数一目了然,asd:asd[1],只对出现的次数进行统计，如果为asd：asd[0]，则对词语进行统计
#如果是d.items(),则只对词语进行操作。
for key in sorted(d.iteritems(),key=lambda asd:asd[1],reverse=True):
    result+=str(key)#+str(d[key])+" "
    print key#(key,d[key])
print('词频统计完成！')
print('排序！')

#print('显示频率前五十的词！')
#print(plt.keys()[:50]) # 查看text1中频率最高的前50个词，FreeDist([])用来计算列表中元素的频率
for key in sorted(d.iteritems(),key=lambda asd:asd[1],reverse=True):
   # temp=dict(key)
    temp=str(key)
    if 'N' in temp:
        classify_n+=temp
    elif 'A' in temp:
        classify_a+=temp
    elif 'AD'in temp:
        classify_ad+=temp
    elif 'AG'in temp:
        classify_an+=temp
    elif 'AL'in temp:
        classify_al+=temp
    elif 'AN'in temp:
        classify_an+=temp
    elif 'D' in temp:
         classify_v+=temp

f=open("t_with_cipin.txt","w")  #将结果保存到另一个文档中
result=result.decode("unicode-escape")
f.write(result)#.encode(encoding='utf-8')

f=f=open("t_with_cipin_n.txt","w")  #将名词保存到另一个文档中
classify_n=classify_n.decode("unicode-escape")
f.write(classify_n)#.encode(encoding='utf-8')

f=f=open("t_with_cipin_a.txt","w")  #将形容词保存到另一个文档中
classify_a=classify_a.decode("unicode-escape")
f.write(classify_a)#.encode(encoding='utf-8')
f=f=open("t_with_cipin_ad.txt","w")  #将形容词保存到另一个文档中
classify_ad=classify_ad.decode("unicode-escape")
f.write(classify_ad)#.encode(encoding='utf-8')
f=f=open("t_with_cipin_ag.txt","w")  #将形容词保存到另一个文档中
classify_ag=classify_ag.decode("unicode-escape")
f.write(classify_ag)#.encode(encoding='utf-8')
f=f=open("t_with_cipin_al.txt","w")  #将形容词保存到另一个文档中
classify_al=classify_al.decode("unicode-escape")
f.write(classify_al)#.encode(encoding='utf-8')
f=f=open("t_with_cipin_an.txt","w")  #将形容词保存到另一个文档中
classify_an=classify_an.decode("unicode-escape")
f.write(classify_an)#.encode(encoding='utf-8')

f=f=open("t_with_cipin_d.txt","w")  #将动词保存到另一个文档中
classify_v=classify_v.decode("unicode-escape")
f.write(classify_v)#.encode(encoding='utf-8')

f.close()
