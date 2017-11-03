#coding=utf-8

# 处理训练文本,生成json格式的频数表

import json
import time
import os

start = time.time()

def get_v_w_dic(filename):
    # 读拼音汉字表,分别生成以拼音和汉字为索引的字典
    dict_v = {}
    dict_w = {}
    f = open(filename,'r',encoding='gbk')
    for line in f:
        line = line.split()
        voice = line[0]
        line.pop(0)
        dict_v[voice] = line
        for word in line:
            if word in dict_w:
                dict_w[word].append(voice)
            else:
                dict_w[word] = []
                dict_w[word].append(voice)
    f.close()
    return dict_v,dict_w

def getdata(filename):
    # 读json格式的新闻稿
    lines = []
    data = []
    f = open(filename,'r')
    lines = [line for line in f]
    f.close()
    data = [json.loads(line) for line in lines] #json.loads比较好的一种用法.
    return data

def build_tree_from_str(TheString,TheTree,count):
    #从单条字符串生成频次树
    #其实这里写到一半想起应该定义一个类,但是想了想其实也就用一次,没啥意义……(所以函数有点长
    N = len(TheString)
    i = 0
    while i < N-1:
        w1 = TheString[i]
        w2 = TheString[i+1]
        if w2 not in dict_w:    #因为标点总是出现在文字后面,所以先判断w2比较好.
            i += 1
            continue
        if w1 not in dict_w:
            i += 1
            continue
        v1 = dict_w[w1]
        v2 = dict_w[w2]
        for i_v1 in v1:
            count += 1
            if i_v1 in TheTree:
                Son1 = TheTree[i_v1] #第一层,如果子节点存在,使用这个子节点
            else:
                TheTree[i_v1] = {} #第一层,如果子节点不存在,建立这个字节点
                Son1 = TheTree[i_v1] #使用新建立的子节点
            #子1-2
            if w1 in Son1:
                Son2 = Son1[w1]
                Son2['Freq_of_w'] += 1
            else:
                Son1[w1] ={}
                Son2 = Son1[w1]
                Son2['Freq_of_w'] = 1

            #处理句围 bg
            if i == N-2:
                if w2 in Son1:
                    Son2 = Son1[w2]
                    Son2['Freq_of_w'] += 1
                else:
                    Son1[w2] ={}
                    Son2 = Son1[w2]
                    Son2['Freq_of_w'] = 1
            #处理句尾 end

            #子2-3
            for i_v2 in v2:
                vv = i_v1 + i_v2
                if vv in Son2:
                    Son3 = Son2[vv]
                else:
                    Son2[vv] = {}
                    Son3 = Son2[vv]
                ww = w1+w2
                if ww in Son3:
                    Son3[ww] += 1
                else:
                    Son3[ww] = 1
        i += 1
    return(TheString,TheTree,count)


def train_tree(InFile, TheTree, OutFile,count):
    # 循环单条字符串生成树的函数, 用来处理单个文件
    start = time.time()
    itr = 0
    data = getdata(InFile)
    for line in data:
        title = line['title']
        content = line['html']
        TheString,TheTree,count = build_tree_from_str(title,TheTree,count)
        TheString,TheTree,count = build_tree_from_str(content,TheTree,count)

        time1 = time.time()-start
        itr += 1
        print(str(itr),time1)

        if time1 > 3600:
            break # 假如处理单个文件超过一个小时,超时退出.

    with open(OutFile,'w') as f:
        json.dump(TheTree,f)
    f.close()
    return(TheTree,count)

filename = '拼音汉字表.txt'
dict_v,dict_w = get_v_w_dic(filename)

time1 = time.time()-start
print('准备完毕',time1)

Freq_Tree = {}
count = 0 #count 用来计数,看看统计了多少个汉字
#循环处理所有文件

for i in range(11):
    i += 1
    father_path=os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")
    pathname = father_path+'/sina_news/'
    InFile =pathname+ '2016-'+'%02d'%i+'.txt'
    OutFile = 'train-'+'%02d'%i+'.json'
    Freq_Tree,count = train_tree(InFile, Freq_Tree, OutFile,count)
    if i > 2:
        del_i = i-2
        del_f = open('train-'+'%02d'%del_i+'.json','w')#及时删除没用的文件


#文件处理完成后,生成Freq_Tree.json.训练生成的缓存文件大部分删掉了,为了防止我的小渣电脑突然蹦,没有全部删掉..
single_Tree = {}
for Key_v1 in Freq_Tree:
    Q = 1
    Tree1 = Freq_Tree[Key_v1]
    for Key_w1 in Tree1:
        Tree2 = Tree1[Key_w1]
        if Tree2['Freq_of_w'] > Q:
            Q = Tree2['Freq_of_w']
            TheWord = Key_w1
    single_Tree[Key_v1] = TheWord


    tf = open('Freq_Tree.json','w')#清空Freq_Tree
    tf.close()
with open('Freq_Tree.json','a') as f:
    json.dump({'all_word':count},f)
    f.write('\n')
    json.dump(single_Tree,f)
    f.write('\n')
    json.dump(Freq_Tree,f)
    f.write('\n')
    f.close()


print('trainer finished')