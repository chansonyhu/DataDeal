# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 09:05:03 2019

@author: Shuo Wan
"""

import json
import datetime
import pandas as pd

#将最初的excel数据取目标属性列，转化为字典数据并返回
def excel_to_dict(filename="forest life用户.xls",interest_columns=['国家码','所属楼盘','注册时间']):
    #对表头属性进行判断设置
    data_original = pd.read_excel(filename,header=0)
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
    data_dict={col:data_interest[col].dropna().tolist() for col in data_interest.columns}            
    
    return data_dict

#辅助函数，由字符串格式的起止日期生成一个datetime格式的待统计月份列表，间隔为月
def generate_list(begin_date,end_date):
    date_list=[]
    temp=list(pd.date_range(start=begin_date, end=end_date,freq='M'))
    for x in temp:
        date_str=x.strftime('%Y-%m-%d')
        date_t=datetime.datetime.strptime(date_str,"%Y-%m-%d")
        date_list.append(datetime.datetime(date_t.year,date_t.month,1,0,0))
    
    return date_list

#统计用户在国家地区层面上的分布，结果转为json存储
def country_distribute_aly(data):
    data_country=data['国家码']
    #读取国家码对照文件，用于最终将国家码转为国家名
    country_no=pd.read_excel("国家码.xls")
    dict_country = country_no.set_index('国家码').T.to_dict('list')
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
    
    with open('country_distribute.json', 'w') as f:
        json.dump(country_freq_byname, f)
    
    return country_freq_byname
        

#统计用户数在楼盘块中的分布
def loupan_distribute_aly(data):
    data_loupan=data['所属楼盘']
    loupan_freq={}
    for loupan in set(data_loupan):
        loupan_freq[loupan]=data_loupan.count(loupan)
    loupan_sort=dict(sorted(loupan_freq.items(), key=lambda e: e[1],reverse=True))
    del loupan_freq, data_loupan
    with open('loupan_distribute.json','w') as f:
        json.dump(loupan_sort,f)
    
    return loupan_sort


#统计用户数在指定时间段内的分布
def date_distribute_aly(data,start_date,end_date):
    data_time=data['注册时间']
    date_list_month=[]
    #将所有字符型日期数据转为指定格式数据，去除天，保留年月
    for date in data_time:
        if type(date)==str:
            date_t=datetime.datetime.strptime(date,"%Y-%m-%d")
            date_list_month.append(datetime.datetime(date_t.year,date_t.month,1,0,0))
    #生成目标日期列表
    target_date=generate_list(start_date,end_date)
    date_freq={}
    
    #统计并存储
    for date in target_date:
        date_freq[date.strftime("%Y-%m")]=date_list_month.count(date)
    with open('date_distribute.json','w') as f:
        json.dump(date_freq,f)
      
    return date_freq



if __name__ == '__main__':
    data_dict=excel_to_dict()
    country_distribute=country_distribute_aly(data_dict)
    loupan_distribute=loupan_distribute_aly(data_dict)
    date_distribute=date_distribute_aly(data_dict,"2018-1","2019-8")
