# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 15:18:53 2019

@author: Shuo Wan
"""
import json
import datetime
import pandas as pd
import re
import numpy as np


def key_analysis(sale_key):
    renew_key={}
    for lab in sale_key:
        split_p=re.search('[\u4e00-\u9fa5] [a-zA-Z]',lab,re.A)
        if not (split_p is None):
            h=split_p.span()[0]+1
            Chinese=lab[0:h+1]
            English=lab[h+1:]
            if len(English)<=2:
                English=Chinese
            else:
                English=English.strip()
        else:
            Chinese=lab
            English=Chinese
        renew_key[lab]=[Chinese,English]
                    
    return renew_key


#对脏标签进行处理，去掉同一家店的其它标签
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
    end_date=datetime.datetime.strptime(end_date,"%Y-%m")
    end_date=end_date+datetime.timedelta(days=31)
    date_list=[]
    temp=list(pd.date_range(start=begin_date, end=end_date,freq='m'))
    for x in temp:
        date_list.append(x.strftime('%Y-%m'))
#        date_t=datetime.datetime.strptime(date_str,"%Y-%m-%d")
#        date_list.append(datetime.datetime(date_t.year,date_t.month,1,0,0))
    
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


def date_distribute_aly(data,sale_set,start_date,end_date,num=30):
    data_time=data['销券时间']
    row=data_time.index
    if len(data_time[row[0]])>=12:
        date_form="%Y-%m-%d %H:%M"
    else:
        date_form="%Y-%m-%d"
    #将所有字符型日期数据转为指定格式数据，去除天，保留年月
    data['销券时间'] = pd.to_datetime(data_dict['销券时间'], format=date_form)
    data['month']=data['销券时间']
    data['month'] =data['month'].apply(lambda x:x.strftime('%Y-%m'))
    data['day']=data['销券时间']
    data['day'] =data['day'].apply(lambda x:x.strftime('%Y-%m-%d'))
   

#    for i in range(len(data_time)):
#        date_t=datetime.datetime.strptime(data_time[row[i]],date_form)
#        data['销券时间'][row[i]]=datetime.datetime(date_t.year,date_t.month,1,0,0)
#        data1['销券时间'][row[i]]=datetime.datetime(date_t.year,date_t.month,date_t.day,0,0)
    month_receive=dict(list(data[['商家名称','month']].groupby('month')))
    day_receive=dict(list(data[['商家名称','day']].groupby('day')))
   
    target_month=generate_list(start_date,end_date)
    
    target_day=[]
    now=datetime.date.today()
    target_day.append(now.strftime('%Y-%m-%d'))
    for i in range(num):
        now=now+datetime.timedelta(days=-1)
        target_day.append(now.strftime('%Y-%m-%d'))
#    target_date=generate_list(start_date,end_date)
    
    target_day.reverse()

    date_freq={}
    key_set=month_receive.keys()
    renew_key=key_analysis(sale_set)
    for date in target_month:
        if date in key_set:
            date_freq[date]={}
            sale_distribute=list(month_receive[date]['商家名称'])
            total_sale=len(sale_distribute)
            date_freq[date]['count']=total_sale
            date_freq[date]['Chinese']={}
            date_freq[date]['English']={}
            for sale in sale_set:
                num=sale_distribute.count(sale)
                date_freq[date]['Chinese'][renew_key[sale][0]]=num                
                date_freq[date]['English'][renew_key[sale][1]]=num
#                date_freq[date.strftime("%Y-%m")][sale]=sale_distribute.count(sale)
        else:
            continue
    sale_list=list(data['商家名称'])
    date_freq['sale_pro']={}
    date_freq['Set']=sale_set
    for sale in sale_set:
        date_freq['sale_pro'][renew_key[sale][0]]=sale_list.count(sale)
    
    day_freq={}
    key_set=day_receive.keys()
    renew_key=key_analysis(sale_set)
    count=np.zeros([len(sale_set)])
    for date in target_day:
        if date in key_set:
            day_freq[date]={}
            sale_distribute=list(day_receive[date]['商家名称'])
            No=0
            for sale in sale_set:
                count[No]+=sale_distribute.count(sale)
                day_freq[date][renew_key[sale][0]]=int(count[No])
                No+=1
#                date_freq[date.strftime("%Y-%m")][sale]=sale_distribute.count(sale)
            day_freq[date]=dict(sorted(day_freq[date].items(), key=lambda e: e[1],reverse=True)[:10])
        else:
            day_freq[date]=0
    
#    with open('cupon.json','w') as f:
#        json.dump(date_freq,f)
    
    date={'cupon by month':date_freq,'cupon by day':day_freq}
    
    return date

   



if __name__ == '__main__':
    [data_dict,groupsales]=excel_to_dict()
    
    cupon_distribute=date_distribute_aly(data_dict,groupsales,"2018-10","2019-7")
    with open('cupon.json','w',encoding='utf-8') as f:
        json.dump(cupon_distribute,f,indent=1,ensure_ascii=False)
    del data_dict,groupsales,cupon_distribute
    f.close()


