#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import jieba
import jieba.posseg as pseg
import time
t1=time.time()
f=open("t_with_splitter.txt","r") #读取文本
string=f.read().decode("utf-8")

words = pseg.cut(string) #进行分词
result=""  #记录最终结果的变量
for w in words:
     result+= str(w.word)+"/"+str(w.flag)+" " #加词性标注

f=open("t_with_POS_tag1.txt","w")  #将结果保存到另一个文档中
f.write(result)
f.close()
t2=time.time()
print("分词及词性标注完成，耗时："+str(t2-t1)+"秒。") #反馈结果
