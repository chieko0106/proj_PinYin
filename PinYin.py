#coding=utf-8

import json
import os

#json格式的频数分布文件.默认在根目录下.也可以指定文件.
def imp_Freq_Tree(filename):
    #按照指定格式读取json文件
    f = open(filename,'r')
    lines = [line for line in f]
    f.close()
    data = [json.loads(line) for line in lines]
    all_word = data[0]
    Q_single = data[1]
    Freq_Tree = data[2]
    return(all_word,Q_single,Freq_Tree)
'''
# 设置频次最低限度.出现频率低于这个值的词组不予考虑.
# 避免出现频次非常少的词组影响频率的计算.
# 这个参数可以根据训练数量酌情提高.
'''
Q_bottom_lim = 450

'''
'''
if os.path.exists('Freq_Tree.json'):
    all_word,Q_single,Freq_Tree = imp_Freq_Tree('Freq_Tree.json')
    print('program initiated')
else:
    json_error = 1
    print('Error: File Freq_Tree.json Not Found.')
    while json_error > 0:
        spe_json = input('Please Allocate "Freq_Tree.json" (with filename):')
        if os.path.exists(spe_json):
            json_error = 0
            all_word,Q_single,Freq_Tree = imp_Freq_Tree(spe_json)
            print('program initiated')
            break
        else:
            print('Entered File Not Found.')
            json_error += 1
        if json_error >10:
            print('You have been failing to enter the correct filename for decades !')
            print('I suggest you refer to the readme.txt file to find out what is going on.:)')
            json_error = 1

father_path=os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")
InFile = father_path+'/data/Input.txt'
'''
关于输入文件部分.先使用默认路径,假如默认路径中没有指定的文件,则从控制台输入.
输入数据存入数组PinYin
'''
if os.path.exists(InFile):
    f = open(InFile)
    PinYin = [line for line in f]
    OutPath = father_path+'/data/'
else:
    print('Warning: Defult File Index "data/Input.txt" Not Found')
    print('Directory Specification Needed !')
    user_cata=input('Please Enter the Catalog of the Input File (with filename):')
    if os.path.exists(user_cata):
        f = open(user_cata)
        PinYin = [line for line in f]
        OutPath = os.path.abspath(os.path.dirname(user_cata)+os.path.sep+".")+'/'


'''
关于输出文件部分.先使用输入文件的路径,假如路径下存在同名文件,提示更改路径,或者更改文件名,或者选择Overwrite.
得到输出文件OutFile(指定路径)
'''
if os.path.exists(OutPath+'Output.txt'):
    print('Warning: Defult Output File "Output.txt" Already Exist.')
    print('You Have Following Options:')
    print('1-Change the catalog;2-Change filename')
    print('Press "Enter" if you simply want to overwrite the existing file')
    user_cata=input('Please Enter Your Selection:')
    if user_cata == '1':
        OutPath = input('Please Enter the New Catalog of the Folder (End with "/"):')
        print('The defult output filename is "Output.txt".')
        print('Please notice that the file "Output.txt" under the ENTERED CATALOG may be overwrite.')
        if_change_outputname = input('If you want to CHANGE the name, enter Y.')
        if if_change_outputname == 'Y':
            out_file_name = input('Please enter the output filename:')
        else:
            out_file_name = 'Output.txt'
        OutFile = OutPath + out_file_name
    elif user_cata == '2':
        out_file_name = input('Please Enter the New Name of the Output File:')
        OutFile = OutPath + out_file_name
    else:
        print('The existing file will be overwritten !')
        out_file_name = 'Output.txt'
        OutFile = OutPath + out_file_name
else:
    OutFile = OutPath + 'Output.txt'


'''
#处理输入文件

#拼音转换汉字的时候有两种情形.一种是两个拼音转换成汉字,另一种是已知前面的汉字之后转第二个汉字.
'''
#定义两个拼音转成汉字的函数.



def vv2ww(v1,v2,lamda1,lamda2):

    ww = {}
    key_vv = v1+v2
    if v1 in Freq_Tree:
        Tree1 = Freq_Tree[v1]
    else:
        print('Error: Illegal PinYin in Input File : '+v1)
        return(v1,'ERROR')
    for key_w1 in Tree1:
        Tree2 = Tree1[key_w1]
        if key_vv in Tree2: #考虑v1+v2双拼的情况
            Tree3 = Tree2[key_vv]
            Q_w1 = Tree2['Freq_of_w']
            for key_ww in Tree3:
                if Tree3[key_ww] > Q_bottom_lim:
                    ww[key_ww] = Tree3[key_ww]/Q_w1*lamda1+Q_w1/all_word['all_word']*lamda2
    if ww is None:
        '''
        # 如果没有v1+v2这个组合在语料库中出现,ww为空,那么v1就难以确定.
        # 这其实是语料库不够大的问题.这时候考虑用Q_single,直接认为v1是当前发音下最常见的字.
        # 而且由于是vv的情况,不存在需要算概率,可以认为这个字直接被跳过了.
        '''
        w1 = Q_single[v1]
        return(w1,'Half')
    return(ww,'Found')

#定义当已知前一个汉字求后一个拼音对应汉字的条件概率的函数.
def wv2ww(w1,v1,v2,lamda1,lamda2):
    w2 = {}
    if v2 not in Freq_Tree: # 检查v2是否合法
        print('Error: Illegal PinYin in Input File : '+v2)
        return(v2,'ERROR')
    Tree1 = Freq_Tree[v1]
    Tree2 = Tree1[w1]
    key_vv = v1+v2
    if key_vv in Tree2:
        Tree3 = Tree2[key_vv]
    else:
        return(v2,'NotFound')

    Q_w1 = Tree2['Freq_of_w']
    for key_ww in Tree3:
        key_w2 = key_ww[-1]
        if Tree3[key_ww] > Q_bottom_lim:
            w2[key_w2] = Tree3[key_ww]/Q_w1*lamda1+Q_w1/all_word['all_word']*lamda2
    return(w2,'Found')


def PinYin_2_HanZi(vs,itm_limit=10,lamda1=10,lamda2=30,tmp_list_limit = 15):
    W_P = []
    if len(vs) == 1:
        if vs[0] in Q_single:
            return([Q_single[vs[0]]])
        else:
            print('Error: Illegal PinYin in Input File : '+vs[0])
            return([[vs[0],0]])
    i = 0
    flag = 'ini'
    while i < len(vs)-1:
        v1 = vs[i]
        v2 = vs[i+1]
        if flag == 'ini' or flag == 'NotFound' or flag == 'Half':
            res, flag = vv2ww(v1,v2,lamda1,lamda2)
            if flag == 'Half':
                if W_P is None:
                    W_P = [[res,1] for i in range(itm_limit)]
                else:
                    for i in range(len(W_P)):
                        W_P[i][0] += res
                i += 1
                continue

            if flag == 'Found':
                temp_tuple = sorted(res.items(), key=lambda d:d[1],reverse=True)
                if len(W_P) < 1:
                    ii = 0

                    while len(W_P) < min(itm_limit,len(temp_tuple)):
                        W_P.append([temp_tuple[ii][0],temp_tuple[ii][1]])
                        ii += 1
                else:
                    temp_list = []
                    temp_dict = {}
                    ii = 0
                    while len(temp_list) < min(tmp_list_limit,len(temp_tuple)):
                        temp_list.append([temp_tuple[ii][0],temp_tuple[ii][1]])
                        ii += 1
                    for Old in W_P:
                        for New in temp_list:
                            temp_dict[Old[0]+New[0]] = Old[1]*New[1]
                    temp_tuple = sorted(temp_dict.items(), key=lambda d:d[1],reverse=True)
                    W_P = []
                    ii = 0
                    while len(W_P) < min(itm_limit,len(temp_tuple)):
                        W_P.append([temp_tuple[ii][0],temp_tuple[ii][1]])
                        ii += 1
                i += 1
                continue

            if flag == 'ERROR':
                print('Exit due to input error!')
                break

        if flag == 'Found':
            all_w1 = {}
            for item in W_P:
                w1 = item[0][-1]
                if w1 not in all_w1:
                    all_w1[w1] = {item[0]:item[1]}
                else:
                    tt = all_w1[w1]
                    tt[item[0]] = item[1]
            temp_dict = {}
            for w1 in all_w1:
                res, flag = wv2ww(w1,v1,v2,lamda1,lamda2)
                if flag == 'Found':
                    tt = all_w1[w1]
                    for Old in tt:
                        for New in res:
                            temp_dict[Old+New] = tt[Old]*res[New]
            temp_tuple = sorted(temp_dict.items(), key=lambda d:d[1],reverse=True)
            W_P = []
            ii = 0
            while len(W_P) < min(itm_limit,len(temp_tuple)):
                W_P.append([temp_tuple[ii][0],temp_tuple[ii][1]])
                ii += 1
            i += 1
            continue
        if flag == 'ERROR':
            print('Warning:Input error!')
        i += 1
        continue
    if W_P:
        return(W_P)
    else:
        print('Warning : Sentence Not Found !')
        print(vs)
        print('Check if the sentence is paticular!')
        print('The demo database is based on Sina News, which may limits the performance of transfer.')
        return([['',0]])



f = open(OutFile,'w')
f.close()
f = open(OutFile,'a')
for vs in PinYin:
    '''
    设定限制参数和光滑参数!
    '''
    itm_limit = 100
    lamda1 = 10 #光滑参数.表示条件概率比重.
    lamda2 = 30 #光滑参数.表示P_w1比重.
    tmp_list_limit = 100 #当新的字出现时,求其排列组合,对新的字有一个限制,舍去概率排在后面的部分,以减小计算量.
    '''
    分割vs
    '''
    vs = vs.split()
    '''
    转换
    '''
    All_Out = PinYin_2_HanZi(vs,itm_limit,lamda1,lamda2,tmp_list_limit)
    Out = All_Out[0][0]
    print(Out)
    '''
    写入输出文件
    '''
    f.write(Out+'\n')
f.close()
print('PinYin Finished')
print('Please Check Out the Output File:',OutFile)