# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 15:06:56 2019

@author: Shuo Wan
"""

import json
import datetime
import pandas as pd

def excel_to_dict(filename="forest支付数据.xls",interest_columns=['楼盘','订单支付时间']):
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
    data_dict={col:data_interest.dropna()[col].tolist() for col in data_interest.columns}            
    
    return data_dict


def loupan_distribute_aly(data):
    data_loupan=data['楼盘']
    loupan_freq={}
    for loupan in set(data_loupan):
        loupan_freq[loupan]=data_loupan.count(loupan)
    loupan_sort=dict(sorted(loupan_freq.items(), key=lambda e: e[1],reverse=True))
    del loupan_freq, data_loupan
    with open('paydata_loupan.json','w') as f:
        json.dump(loupan_sort,f)
    
    return loupan_sort

def generate_list(begin_date,end_date):
    date_list=[]
    temp=list(pd.date_range(start=begin_date, end=end_date,freq='M'))
    for x in temp:
        date_str=x.strftime('%Y-%m-%d')
        date_t=datetime.datetime.strptime(date_str,"%Y-%m-%d")
        date_list.append(datetime.datetime(date_t.year,date_t.month,1,0,0))
    
    return date_list

def date_distribute_aly(data,start_date,end_date):
    data_time=data['订单支付时间']
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
    with open('pay_date.json','w') as f:
        json.dump(date_freq,f)
      
    return date_freq


if __name__ == '__main__':
    data_dict=excel_to_dict()
    padata_loupan=loupan_distribute_aly(data_dict)
    date_distribute=date_distribute_aly(data_dict,"2019-1","2019-8")