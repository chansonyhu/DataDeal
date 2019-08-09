# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 16:44:05 2019

@author: Shuo Wan
"""

import json
import pandas as pd
import re


def To_chinese(string):
    st=re.sub("[A-Za-z0-9\!\%\[\]\，\ \。\&\-\(\)\'\/]", "", string)
    if len(st)<=1:
        return string.strip()
    else:
        return st.strip()

#读取数据，生成dataframe文件，抓取列和文件名为函数参数
def excel_to_dict(filename,sheet='问卷数据'):
    #对表头属性进行判断设置
    path="data/"
    try:
        data_original = pd.read_excel(path+filename+".xls",header=0,sheet_name=sheet)
    except:
        data_original = pd.read_excel(path+filename+".xlsx",header=0,sheet_name=sheet)
    
    if True in data_original.columns.str.contains('^Unnamed'):

        #获取行列索引
        col=data_original.columns
        row=data_original.index
        #找到第一个不为null的行，即为属性名所在行，设置属性名
        judge_null=data_original[col[0]].isnull()
        for i in range(8):
            if judge_null[i]==False:
                break
        data_original.columns=list(data_original.iloc[i])
        #删除无数据的表头，如果没有表头则跳过
        for j in range(i+1):
            data_original.drop(row[j],inplace=True)
    
    
    #丢掉NULL行并返回
    return data_original



#对一个指定列名进行分布统计
def item_distribute_aly(data,item):
    data_item=list(data[item].dropna())
    total=len(data_item)
    item_freq={}
    item_freq['total']=total
    item_set=set(data_item)
    item_freq['其他']=0
    #数据格式里面对中文和英文分标签
    #如果名称本身不需要分割，则不必进行中英文分割
    for item_d in item_set:
        num=data_item.count(item_d)
        key=To_chinese(item_d)
        if num>=total*0.02:
            item_freq[key]=num
        else:
            item_freq['其他']+=num
    if item_freq['其他']==0:
        item_freq.pop('其他')
    #排序结果对中文和英文分标签
    item_sort=dict(sorted(item_freq.items(), key=lambda e: e[1],reverse=True))

    
    return item_sort

def distribute_accumu(data):
    col=data.columns
    dis_acc={}
    for pt in col:
        key=To_chinese(pt)
        dis_acc[key]=item_distribute_aly(data,pt)
    
    return dis_acc


def distribute_by_item(data,f_item,s_item):
    data_f=list(data[f_item].dropna())
    father_key={}
    num=0
    for f in set(data_f):
        num+=1
        father_key[f]=data_f.count(f)
    if num>=5 and not(f_item=='年龄'):
        num=5
    main_f=dict(sorted(father_key.items(), key=lambda e: e[1],reverse=True)[:num]).keys()
    dict_receive=dict(list(data.groupby(f_item)))
    father_freq={}
    father_freq['Set']=[]
    
    for f in main_f:
        fc=To_chinese(f)
        dis=item_distribute_aly(dict_receive[f].copy(),s_item)
        if not dis:
            continue
        father_freq[fc]=dis
        father_freq['Set'].append(fc)
        
      
    return father_freq

def interplay(data,filename='sale data',sheet='关联设置'):
    path="data/"
    try:
        require_inter = pd.read_excel(path+filename+".xls",header=0,sheet_name=sheet)
    except:
        require_inter = pd.read_excel(path+filename+".xlsx",header=0,sheet_name=sheet)
    
    if require_inter.empty:
        return 1
    
    row=require_inter.index
    inter={}
    
    for i in row:
        father=require_inter['父属性'][i]
        son=require_inter['子属性'][i]
        inter[son+' in '+father]=distribute_by_item(data,father,son)
        
        
    return inter
    




if __name__ == '__main__':
    data=excel_to_dict(filename="sale data")
    dis_acc=distribute_accumu(data)
    dis_inter=interplay(data)
    sale_statistics={}
    sale_statistics['分布']=dis_acc
    if not(dis_inter==1):
        sale_statistics['关联分析']=dis_inter
    with open('data/sale.json','w',encoding='utf-8') as f:
        json.dump(sale_statistics,f,indent=1,ensure_ascii=False)
    f.close()

    
