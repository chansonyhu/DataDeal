# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 15:18:53 2019

@author: Shuo Wan
"""
import json
import datetime
import pandas as pd



def remove_similar_index(groupsales,data):
    similaridx=[]
    delet_label=[]
    numsales=len(groupsales)
    for i in range(numsales):
        for j in range(numsales):
            if i==j:
                continue
            if groupsales[i] in groupsales[j]:
                similaridx.append([i,j])
    len_similar=len(similaridx)
    if len_similar==0:
        return [data, groupsales]
    for i in range(len_similar):
        idx=similaridx[i]
        delet_label.append(groupsales[idx[0]])
        data.replace(groupsales[idx[0]],groupsales[idx[1]],inplace=True)
    for labels in delet_label:
        groupsales.remove(labels)
    return [data,groupsales]


def generate_list(begin_date,end_date):
    date_list=[]
    temp=list(pd.date_range(start=begin_date, end=end_date,freq='M'))
    for x in temp:
        date_str=x.strftime('%Y-%m-%d')
        date_t=datetime.datetime.strptime(date_str,"%Y-%m-%d")
        date_list.append(datetime.datetime(date_t.year,date_t.month,1,0,0))
    
    return date_list

def excel_to_dict(filename="收楼优惠券.xls",interest_columns=['商家名称','销券时间']):
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
    data=data_interest.dropna()
    groupsales=list(set(list(data['商家名称'].values)))
    [data,groupsales]=remove_similar_index(groupsales,data)
    #将dateframe格式转为字典，每个列名作为一个字典的key
#    data_dict={col:data_interest.dropna()[col].tolist() for col in data_interest.columns}            
    
    return [data,groupsales]


def date_distribute_aly(data,sale_set,start_date,end_date):
    data_time=data['销券时间']
    row=data_time.index
    #将所有字符型日期数据转为指定格式数据，去除天，保留年月
    for i in range(len(data_time)):
        date_t=datetime.datetime.strptime(data_time[row[i]],"%Y-%m-%d")
        data['销券时间'][row[i]]=datetime.datetime(date_t.year,date_t.month,1,0,0)
    dict_receive=dict(list(data.groupby('销券时间')))
    target_date=generate_list(start_date,end_date)
    date_freq={}
    key_set=dict_receive.keys()
    for date in target_date:
        if date in key_set:
            date_freq[date.strftime("%Y-%m")]={}
            sale_distribute=list(dict_receive[date]['商家名称'])
            total_sale=len(sale_distribute)
            date_freq[date.strftime("%Y-%m")]['count']=total_sale
            for sale in sale_set:
                date_freq[date.strftime("%Y-%m")][sale]=sale_distribute.count(sale)/total_sale
        else:
            date_freq[date.strftime("%Y-%m")]=0
    sale_list=list(data['商家名称'])
    date_freq['sale_pro']={}
    date_freq['sale_set']=sale_set
    for sale in sale_set:
        date_freq['sale_pro'][sale]=sale_list.count(sale)
    with open('cupon.json','w') as f:
        json.dump(date_freq,f)
      
    return date_freq




if __name__ == '__main__':
    [data_dict,groupsales]=excel_to_dict()
    cupon_distribute=date_distribute_aly(data_dict,groupsales,"2019-5","2019-8")
