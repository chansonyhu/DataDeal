# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:29:23 2019

@author: Shuo Wan
"""
import json
import datetime
import pandas as pd
import re


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


def generate_list(begin_date,end_date):
    end_date=datetime.datetime.strptime(end_date,"%Y-%m")
    end_date=end_date+datetime.timedelta(days=31)
    date_list=[]
    temp=list(pd.date_range(start=begin_date, end=end_date,freq='M'))
    for x in temp:
        date_list.append(x.strftime('%Y-%m'))
#        date_t=datetime.datetime.strptime(date_str,"%Y-%m-%d")
#        date_list.append(datetime.datetime(date_t.year,date_t.month,1,0,0))
    
    return date_list

def excel_to_dict(filename="预约收楼.xls",interest_columns=['楼盘名称','预约时间']):
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

def date_distribute_aly(data,start_date,end_date):
    data_time=data['预约时间']
    row=data_time.index
    if len(data_time[row[0]])>=12:
        date_form="%Y-%m-%d %H:%M"
    else:
        date_form="%Y-%m-%d"

    data['预约时间'] = pd.to_datetime(data_dict['预约时间'], format=date_form)
    data['预约时间'] =data['预约时间'].apply(lambda x:x.strftime('%Y-%m'))


    #将所有字符型日期数据转为指定格式数据，去除天，保留年月
#    for i in range(len(data_time)):
#        date_t=datetime.datetime.strptime(data_time[row[i]],date_form)
#        data['预约时间'][row[i]]=datetime.datetime(date_t.year,date_t.month,1,0,0)
    dict_receive=dict(list(data.groupby('预约时间')))
    target_date=generate_list(start_date,end_date)
    date_freq={}
    key_set=dict_receive.keys()
    loupan_set=dict(list(data.groupby('楼盘名称'))).keys()
    date_freq['Set']=list(loupan_set)
    renew_key=key_analysis(date_freq['Set'])
    for date in target_date:
        if date in key_set:
            date_freq[date]={}
            loupan_distribute=list(dict_receive[date]['楼盘名称'])
            total_loupan=len(loupan_distribute)
            date_freq[date]['count']=total_loupan
            date_freq[date]['Chinese']={}
            date_freq[date]['English']={}
            for loupan in loupan_set:
                date_freq[date]['Chinese'][renew_key[loupan][0]]=loupan_distribute.count(loupan)
                date_freq[date]['English'][renew_key[loupan][1]]=loupan_distribute.count(loupan)
        else:
            continue
    
    with open('data/reserve_apartment.json','w',encoding='utf-8') as f:
        json.dump(date_freq,f,indent=1,ensure_ascii=False)
      
    return date_freq


if __name__ == '__main__':
    data_dict=excel_to_dict()
    date_distribute=date_distribute_aly(data_dict,"2015-10","2019-8")