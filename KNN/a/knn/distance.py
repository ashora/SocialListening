# -*- coding:utf-8 -*-
'''
 * 语义距离
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from jpype import *

startJVM(getDefaultJVMPath(),"-Djava.class.path=E:\python\hanlp\hanlp-1.2.8.jar;E:\python\hanlp", "-Xms512m", "-Xmx512m")#Xms1g,Xmx1g,指定内存
HanLP = JClass('com.hankcs.hanlp.dictionary.CoreSynonymDictionary')
f1_list=[]
f2_list=[]
f1 = open('training set/wuliusudu_Z.txt','r')#检验级文件名
for i in f1.readlines():
    f1_list.append(i.strip())
f2 = open('daijianyan_1','r')#待分类文件名
for i in f2.readlines():
    f2_list.append(i.strip())



a=""
b=""
results_yanse=""
for a in f1_list:
    for b in f2_list:
        if HanLP.similarity(a,b)>=0.99:#语义相似度大于0.99
            if HanLP.distance(a, b)<=100000:#语义距离小于100000
                results_yanse+=("\n")+str(b)#转行添加
                print(a + "\t" + b + "\t的相似度是\t" +str(HanLP.similarity(a,b))+"\t的词义距离是\t"+str(HanLP.distance(a, b)))
                 # HanLP.Dictionary.CoreSynonymDictionary.distance(a, b))
                # print(a + "\t" + b + "\t的相似度是\t" +str(HanLP.similarity(a,b)))

f3 = open('training set/wuliusudu_Z.txt','a')#在检验级文本后追加符合相似度大于0.99，距离相遇100000的词语
f3.write(results_yanse)

f1.close()
f2.close()
f3.close()
