# -*- coding: utf-8 -*-
'''
@ 文件功能描述：分析学选考的成绩报告单
@ 创建日期：2023年2月24日
@ 创建人：杨再兴
'''
import pdfplumber
import os,re
from os import path
import pandas as pd
#扫描pdf文件
def scaner_file(dire,_file_list):    
    file  = os.listdir(dire)
    ptn = re.compile('.*\.pdf')    
    for f in file:
        real_path = path.join (dire , f)
        if path.isfile(real_path):
            d=path.abspath(real_path)# 如果是文件，则以绝度路径的方式输出
            res = ptn.match(d)
            if (res != None):
                _file_list.append(d)
        elif path.isdir(real_path):
            #如果是目录，则是地柜调研自定义函数 scaner_file (url)进行多次
            scaner_file(real_path,_file_list)
        else:
            print("其他情况")
            pass
    # return _file_list
#提取pdf中的excel
def read_pdf2excel(_path):
    con=[]
    with pdfplumber.open(_path) as pdf:        
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            table = page.extract_table()
            if table is not None:
                con.append(table)
    return con

def sigle_page_info(info):
    dic={}           
    dic["姓名"]=info[1][1]
    dic["科目"]=info[2][1]
    dic["考号"]=info[2][3]
    dic["等级赋分"]=info[1][5]
    dic["层级1"]=str_split(info[5][1])
    dic["层级2"]=str_split(info[6][1])
    dic["层级3"]=str_split(info[7][1])
    dic["层级4"]=str_split(info[8][1])
    dic["层级5"]=str_split(info[9][1])    
    return dic
def str_split(s):
    # s=s.replace("-","")
    if s!="--":
        s=s.replace('第' , '').replace('题' , '')
        pattern = re.compile(r'[\s\n\t\r]+')
        s=re.sub(pattern,"", s)
        l=s.split(',')
    else:
        l=None
    return l


#生成题目的分值，层级系数的字典
# def fs():
    
#     timu={}
#     for i in range(len(liehao)):
#         timu[liehao[i]]=[i,mf[i]]
#     cengji={}
#     for i in range(len(cj)):
#         cengji[cj[i]]=cj_xs[i]
#     return timu,cengji


#把每一层级的题目拆分出来
def transpose_matrix(jsxk,th,xk,cj):
    cjfx={}
    for i in jsxk[:]:
        # transpose_matrix(_xk_info)
        #题号提取，每题的分值
        tmsl=th[i]
        if tmsl is not None:
            mi=matrix_index(tmsl)
            xk_info=xk[i]
            arr=[[""]*(len(tmsl)+2) for i in range(len(xk_info))]
            for j in range(len(xk_info)):
                info=xk_info[j]
                arr[j][0]=info["姓名"]
                arr[j][1]=info["等级赋分"]
                for cj_ in cj:                
                    cjinfo=info[cj_]
                    k=0
                    while cjinfo is not None and k<len(cjinfo):
                        xuhao=cjinfo[k]                      
                        index=mi[xuhao]
                        arr[j][2+index]=cj_
                        k=k+1
                cjfx[i]=arr
        else:
            return "key error,没这学科"
    return cjfx
        
def tiqu_tihao(xk,cj):#提取各科目的题号    
    km={}
    for x in xk:
        y=xk[x][0]
        tm=[]
        if y[cj[0]] is not None:tm=tm+y[cj[0]]
        if y[cj[1]] is not None:tm=tm+y[cj[1]]
        if y[cj[2]] is not None:tm=tm+y[cj[2]]
        if y[cj[3]] is not None:tm=tm+y[cj[3]]
        if y[cj[4]] is not None:tm=tm+y[cj[4]]
        tm.sort(key=lambda l: int(re.findall('\d+', l)[0]))
        km[x]=tm
    return km
def matrix_index(th):
    dic={}
    for i in range(len(th)):
        dic[th[i]]=i
    return dic

    
def main(pdf_directon,jsxk):
    if pdf_directon is None or len(pdf_directon) ==0 or jsxk is None or len(jsxk)==0:return "输入有误"
    fl=[]#pdf的文件路径列表
    
    scaner_file(pdf_directon,fl)
    
    pdf_list=[]#读取的pdf内容列表，一个pdf一行
    for _path in fl:
        pdf=read_pdf2excel(_path)
        pdf_list.append(pdf)
        
    info_list=[]#提取pdf信息，按个人存储
    for one in pdf_list:
        d=[]
        for p in one:
            if p is not None:
                d.append(sigle_page_info(p))
        info_list.append(d)
        
    xk={}#按学科存储
    for one in info_list:
        for p in one:
            if p["科目"] in xk:
                xk[p["科目"]].append(p)
            else:
                xk[p["科目"]]=[p] 
                
                
    cj=['层级1','层级2','层级3','层级4','层级5']
    th=tiqu_tihao(xk,cj)
    
    
    gkcj=transpose_matrix(jsxk,th,xk,cj)
    

    for i in gkcj:
        s=["姓名","等级赋分"]
        df=pd.DataFrame(gkcj[i],columns=s+th[i])
        df=df.sort_values("等级赋分",ascending=False)
        ckcjtj=[]
        xkcjinfo=gkcj[i]
        for o in range(2,len(xkcjinfo[0])):            
            dic={}
            for p in range(len(xkcjinfo)):                
                dic[xkcjinfo[p][o]]=dic.get(xkcjinfo[p][o],0)+1
            ckcjtj.append(dic)
        df2=pd.DataFrame(ckcjtj,columns=cj,index=th[i])
        df2=df2.T
        df3=df2/df2.sum()
        
        
        writer=pd.ExcelWriter("首考赋分分析_"+str(i)+".xlsx")
        df.to_excel(excel_writer=writer,sheet_name='首考原始数据解析',index=False)
        df3.to_excel(excel_writer=writer,sheet_name='各题等级分析',index=True)       
        writer.save()
    

if __name__ == '__main__':
    pdf_directon=r"D:\桌面\成绩报告单分析程序\2023年1月首考成绩报告单"
    jsxk=['信息技术','通用技术']
    main(pdf_directon,jsxk)

        
     
        
 