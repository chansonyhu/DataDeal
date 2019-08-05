# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 14:36:12 2019

@author: Shuo Wan
"""

import json
import datetime
import pandas as pd

#读取数据，生成dataframe文件，抓取列和文件名为函数参数
def excel_to_dict(filename,interest_columns):
    #对表头属性进行判断设置
    path="data/"
    try:
        data_original = pd.read_excel(path+filename+".xls",header=0)
    except:
        data_original = pd.read_excel(path+filename+".xlsx",header=0)
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
    
    #取出感兴趣的属性列
    data_interest=data_original[interest_columns]
    
    #丢掉NULL行并返回
    return data_interest.dropna()

#根据起止月份，产生一个月份列表，输入输出都为年-月格式的字符串
def generate_list(begin_date,end_date):
    end_date=datetime.datetime.strptime(end_date,"%Y-%m")
    end_date=end_date+datetime.timedelta(days=31)
    date_list=[]
    temp=list(pd.date_range(start=begin_date, end=end_date,freq='m'))
    for x in temp:
        date_list.append(x.strftime('%Y-%m'))
    
    return date_list


#对一个指定列名进行分布统计
def item_distribute_aly(data,item):
    data_item=list(data[item])
    item_freq={}
    item_set=set(data_item)
    #数据格式里面对中文和英文分标签
    #如果名称本身不需要分割，则不必进行中英文分割
    for item_d in item_set:
        item_freq[item_d]=data_item.count(item_d)
    #排序结果对中文和英文分标签
    item_sort=dict(sorted(item_freq.items(), key=lambda e: e[1],reverse=True))

    
    return item_sort

#需要对日期项目保留年月再统计，对日期列分布进行统计
def date_distribute_aly(data,item):
    start_date="2015-1"
    data_time=data[item]
    row=data_time.index
    if len(data_time[row[0]])>=12:
        date_form="%Y-%m-%d %H:%M"
    else:
        date_form="%Y-%m-%d"

    
    data['month'] = pd.to_datetime(data[item], format=date_form)
    data['month'] =data['month'].apply(lambda x:x.strftime('%Y-%m'))

    
    date_set=list(set(list(pd.to_datetime(data['month'],format='%Y-%m'))))
    date_set.sort()
    e_date=date_set[-1]
    end_date=e_date.strftime("%Y-%m")
    #生成目标日期列表
    target_date=generate_list(start_date,end_date)
    date_freq={}
    
    #统计并存储
    flag=0
    for date in target_date:
        num=list(data['month']).count(date)
        if num>0:
            flag=1
        if flag==1:
            date_freq[date]=num
      
    return date_freq

def distribute_by_date(data,d_item,item):
    start_date="2016-1"
    data_time=data[d_item]
    row=data_time.index
    if len(data_time[row[0]])>=12:
        date_form="%Y-%m-%d %H:%M"
    else:
        date_form="%Y-%m-%d"

    data['month'] = pd.to_datetime(data[d_item], format=date_form)
    data['month'] =data['month'].apply(lambda x:x.strftime('%Y-%m'))
    
    lmonth=list(set(list(pd.to_datetime(data['month'],format='%Y-%m'))))
    lmonth.sort()
    end_date=lmonth[-1].strftime("%Y-%m")


    dict_receive=dict(list(data.groupby('month')))
    target_date=generate_list(start_date,end_date)
    date_freq={}
    key_set=list(dict_receive.keys())
    item_set=list(dict(list(data.groupby(item))).keys())
    date_freq['Item_Set']=item_set
    date_freq['Date_Set']=key_set
    
    flag=0
    for date in target_date:
        if date in key_set:
            flag=1
        if flag==1:
            date_freq[date]={}
            item_distribute=list(dict_receive[date][item])
            total_item=len(item_distribute)
            date_freq[date]['count']=total_item
            for target_item in item_set:
                date_freq[date][target_item]=item_distribute.count(target_item)
    
      
    return date_freq






if __name__ == '__main__':
    data=excel_to_dict(filename="forest支付数据",interest_columns=['楼盘','订单支付时间'])
    loupan_dis=item_distribute_aly(data,'楼盘')
    time_dis=date_distribute_aly(data,'订单支付时间')
    date_freq=distribute_by_date(data,'订单支付时间','楼盘')
    
    
    
    
    
    