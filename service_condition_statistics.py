# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 15:06:56 2019

@author: Shuo Wan
"""

import json
import datetime
import pandas as pd
import re

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
#    data_dict={col:data_interest.dropna()[col].tolist() for col in data_interest.columns}            
    
    return data_interest.dropna()

def key_analysis(loupan_key):
    renew_key={}
    for lab in loupan_key:
        split_p=re.search('P\d',lab)
        if not (split_p is None):
            h=split_p.span()[1]
            Chinese=lab[0:h+1]
            English=lab[h+1:]
            if len(English)<=2:
                English='Demo'
            else:
                English=English.strip()
        else:
            Chinese=lab
            English='Demo'
        renew_key[lab]=[Chinese,English]
                    
    return renew_key


def loupan_distribute_aly(data):
    data_loupan=list(data['楼盘'])
    loupan_freq={}
    for loupan in set(data_loupan):
        loupan_freq[loupan]=data_loupan.count(loupan)
    loupan_sort=dict(sorted(loupan_freq.items(), key=lambda e: e[1],reverse=True))
    del loupan_freq, data_loupan
#    with open('paydata_loupan.json','w') as f:
#        json.dump(loupan_sort,f)
    
    return loupan_sort

def generate_list(begin_date,end_date):
    end_date=datetime.datetime.strptime(end_date,"%Y-%m")
    end_date=end_date+datetime.timedelta(days=31)
    date_list=[]
    temp=list(pd.date_range(start=begin_date, end=end_date,freq='M'))
    for x in temp:
        date_list.append(x.strftime('%Y-%m'))
    
    return date_list

def date_distribute_aly(data,start_date,end_date,num=2):
    data_time=data['订单支付时间']
    row=data_time.index
    if len(data_time[row[0]])>=12:
        date_form="%Y-%m-%d %H:%M"
    else:
        date_form="%Y-%m-%d"


    data['订单支付时间'] = pd.to_datetime(data_dict['订单支付时间'], format=date_form)
    data['订单支付时间'] =data['订单支付时间'].apply(lambda x:x.strftime('%Y-%m'))
    date_list_month=list(data['订单支付时间'])
    

    target_date=generate_list(start_date,end_date)
    date_freq={}
    date_set=set(date_list_month)
    
    #统计并存储
    for date in target_date:
        if date in date_set:
            date_freq[date]=date_list_month.count(date)
        
    dict_receive=dict(list(data.groupby('订单支付时间')))
    target_date=[]
    now=datetime.date.today()
    target_date.append(now.strftime('%Y-%m'))
    for i in range(num):
        now=now+datetime.timedelta(days=-(now.day+2))
        target_date.append(now.strftime('%Y-%m'))
    month_freq={}
    key_set=dict_receive.keys()
    loupan_set=dict(list(data.groupby('楼盘'))).keys()
    renew_key=key_analysis(list(loupan_set))
    for date in target_date:
        if date in key_set:
            month_freq[date]={}
            month_freq[date]['Chinese']={}
            month_freq[date]['English']={}
            lou=list(dict_receive[date]['楼盘'])
            for loupan in loupan_set:
                num=lou.count(loupan)
                month_freq[date]['Chinese'][renew_key[loupan][0]]=num
                month_freq[date]['English'][renew_key[loupan][1]]=num
        else:
            continue

#    with open('pay_date.json','w') as f:
#        json.dump(date_freq,f)
      
    return [date_freq,month_freq]


if __name__ == '__main__':
    data_dict=excel_to_dict()
    padata_loupan=loupan_distribute_aly(data_dict)
    [date_distribute,month_freq]=date_distribute_aly(data_dict,"2019-1","2019-7")
    with open('pay_data.json','w',encoding='utf-8') as f:
        json.dump({'loupan':padata_loupan,'date':date_distribute,'month':month_freq},f,indent=1,ensure_ascii=False)
