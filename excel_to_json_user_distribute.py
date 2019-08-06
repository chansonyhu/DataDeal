# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 09:05:03 2019

@author: Shuo Wan
"""

import json
import datetime
import pandas as pd
import re

#将最初的excel数据取目标属性列，转化为字典数据并返回
def excel_to_dict(filename="forest life用户",interest_columns=['国家码','所属楼盘','注册时间']):
    #对表头属性进行判断设置
    path="data/"
    try:
        data_original = pd.read_excel(path+filename+".xls",header=0)
    except:
        data_original = pd.read_excel(path+filename+".xlsx",header=0)
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
        #删除无数据错误行
        for j in range(i+1):
            data_original.drop(row[j],inplace=True)
        
    data_interest=data_original[interest_columns]
    #将dateframe格式转为字典，每个列名作为一个字典的key
    data_dict={col:data_interest.dropna()[col].tolist() for col in data_interest.columns}            
    
    return [data_dict,data_interest.dropna()]

#辅助函数，由字符串格式的起止日期生成一个datetime格式的待统计月份列表，间隔为月
def generate_list(begin_date,end_date):
    end_date=datetime.datetime.strptime(end_date,"%Y-%m")
    end_date=end_date+datetime.timedelta(days=31)
    date_list=[]
    temp=list(pd.date_range(start=begin_date, end=end_date,freq='M'))
    for x in temp:
        date_str=x.strftime('%Y-%m-%d')
        date_t=datetime.datetime.strptime(date_str,"%Y-%m-%d")
        date_list.append(datetime.datetime(date_t.year,date_t.month,1,0,0))
    
    return date_list

#统计用户在国家地区层面上的分布，结果转为json存储
def country_distribute_aly(data):
    path="data/"
    data_country=data['国家码']
    #读取国家码对照文件，用于最终将国家码转为国家名
    try:
        country_no=pd.read_excel(path+"国家码.xls")[['国际域名缩写','电话代码']]
    except:
        country_no=pd.read_excel(path+"国家码.xlsx")[['国际域名缩写','电话代码']]
    country_no=country_no.dropna()
    dict_country = country_no.set_index('电话代码').T.to_dict('list')
    del country_no
    
    country_freq={}
    country_freq_byname={}
    #统计各个国家的用户数量
    for country in set(data_country):
        country_freq[country]=data_country.count(country)
    #排序
    country_sort=dict(sorted(country_freq.items(), key=lambda e: e[1],reverse=True))
    del country_freq, data_country
    
    #对照字典，将key由国家号依次换为国家名
    for keys in country_sort.keys():
        newkeys=dict_country[int(keys)][0]
        country_freq_byname[newkeys]=country_sort[keys]
    del country_sort
    
#    with open('country_distribute.json', 'w') as f:
#        json.dump(country_freq_byname, f)
    
    return country_freq_byname
        
#定义楼盘标签处理函数
def key_analysis(loupan_key):
    renew_key={}
    for lab in loupan_key:
        split_p=re.search('P\d',lab)
        if not (split_p is None):
            h=split_p.span()[1]
            Chinese=lab[0:h+1].strip()
            English=lab[h+1:].strip()
            if len(English)<=2:
                English='Demo'
            else:
                English=English.strip()
        else:
            Chinese=lab
            English='Demo'
        renew_key[lab]=[Chinese,English]
                    
    return renew_key

#统计用户数在楼盘块中的分布
def loupan_distribute_aly(data):
    data_loupan=data['所属楼盘']
    loupan_freq_chinese={}
    loupan_freq_english={}
    loupan_set=list(set(data_loupan))
    flag=0
    renew_key=key_analysis(loupan_set)
    for loupan in loupan_set:
        num=data_loupan.count(loupan)
        loupan_freq_chinese[renew_key[loupan][0]]=num
        if renew_key[loupan][1]=='Demo':
            if flag==0:
                loupan_freq_english[renew_key[loupan][1]]=num
                flag=1
                continue
            else:
                loupan_freq_english[renew_key[loupan][1]]+=num
                continue
        
        loupan_freq_english[renew_key[loupan][1]]=num
    loupan_sort_chinese=dict(sorted(loupan_freq_chinese.items(), key=lambda e: e[1],reverse=True))
    loupan_sort_english=dict(sorted(loupan_freq_english.items(), key=lambda e: e[1],reverse=True))
#    with open('loupan_distribute.json','w') as f:
#        json.dump(loupan_sort,f)
    
    return [loupan_sort_chinese,loupan_sort_english]


#统计用户数在指定时间段内的分布
def date_distribute_aly(data,start_date):
    data_time=data['注册时间']
    date_list_month=[]
    #将所有字符型日期数据转为指定格式数据，去除天，保留年月
    for date in data_time:
        date_t=datetime.datetime.strptime(date,"%Y-%m-%d")
        date_list_month.append(datetime.datetime(date_t.year,date_t.month,1,0,0))
    date_set=list(set(date_list_month))
    date_set.sort()
    e_date=date_set[-1]
    end_date=e_date.strftime("%Y-%m")
    #生成目标日期列表
    target_date=generate_list(start_date,end_date)
    date_freq={}
    
    #统计并存储
    flag=0
    for date in target_date:
        num=date_list_month.count(date)
        if num>0:
            flag=1
        if flag==1:
            date_freq[date.strftime("%Y-%m")]=num
#    with open('date_distribute.json','w') as f:
#        json.dump(date_freq,f)
      
    return date_freq



def month_country(data,num=2):
    #将所有字符型日期数据转为指定格式数据，去除天，保留年月
    data['注册时间'] = pd.to_datetime(data_dict['注册时间'], format="%Y-%m-%d")
    data['month']=data['注册时间']
    data['month'] =data['month'].apply(lambda x:x.strftime('%Y-%m'))

#    for i in range(len(data_time)):
#        date_t=datetime.datetime.strptime(data_time[row[i]],"%Y-%m-%d")
#        data['注册时间'][row[i]]=datetime.datetime(date_t.year,date_t.month,1,0,0)
    dict_receive=dict(list(data.groupby('month')))
    path="data/"
    try:
        country_no=pd.read_excel(path+"国家码.xls")[['国际域名缩写','电话代码']]
    except:
        country_no=pd.read_excel(path+"国家码.xlsx")[['国际域名缩写','电话代码']]
    country_no=country_no.dropna()
    dict_country = country_no.set_index('电话代码').T.to_dict('list')

    target_date=[]
    lmonth=list(set(list(data['注册时间'])))
    lmonth.sort()
    now=lmonth[-1]
    
    target_date.append(now.strftime('%Y-%m'))
    for i in range(num):
        now=now+datetime.timedelta(days=-(now.day+2))
        target_date.append(now.strftime('%Y-%m'))
    now=now+datetime.timedelta(days=-(now.day+2))
    start=now.strftime('%Y-%m')
    date_freq={}
    key_set=dict_receive.keys()
    if start in key_set:
        start_c=len(list(dict_receive[start]['国家码']))
    else:
        start_c=0
    target_date.reverse()
    for i in range(len(target_date)):
        date=target_date[i]
        if date in key_set:
            date_freq[date]={}
            country_distribute=list(dict_receive[date]['国家码'])
            total_num=len(country_distribute)
            date_freq[date]['total_num']=total_num
            if i==0:
                date_freq[date]['rise num']=total_num-start_c
            else:
                date_freq[date]['rise num']=total_num-date_freq[target_date[i-1]]['total_num']
            for country in set(country_distribute):
                newkeys=dict_country[int(country)][0]
                date_freq[date][newkeys]=country_distribute.count(country)
        else:
            continue
    return date_freq


if __name__ == '__main__':
    [data_dict,data_frame]=excel_to_dict()
    data_json={}
    data_json['country distribute by month']=month_country(data_frame)
    data_json['Entire country distribute']=country_distribute_aly(data_dict)
    [chinese,english]=loupan_distribute_aly(data_dict)
    data_json['loupan distribute chinese']=chinese
    data_json['loupan distribute english']=english
    data_json['Time distribute']=date_distribute_aly(data_dict,"2017-1")
    with open('data/APPuser_distribute.json','w',encoding='utf-8') as f:
        json.dump(data_json,f,indent=1,ensure_ascii=False)
    f.close()
    del data_dict,data_frame,data_json,chinese,english
    
