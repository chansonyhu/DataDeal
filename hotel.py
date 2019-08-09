# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:50:13 2019

@author: Shuo Wan
"""

import pandas as pd
import numpy as np
import json


def jingying_month(filename='hotel data',sheet="月份经营情况"):
    path="data/"
    try:
        data = pd.read_excel(path+filename+".xls",sheet_name=sheet,header=0)
    except:
        data = pd.read_excel(path+filename+".xlsx",sheet_name=sheet,header=0)
    
    row=data.index
    num_row=len(row)
    sale={}
    for i in range(num_row):
        sale[data['月份'][row[i]]]={}
#        dict['月份']=data['月份'][row[i]]
        sale[data['月份'][row[i]]]['Act 当月']=data['Act 当月'][row[i]]
        sale[data['月份'][row[i]]]['Budget 预算']=data['Budget 预算'][row[i]]
        sale[data['月份'][row[i]]]['Completion Rate预算完成率']=sale[data['月份'][row[i]]]['Act 当月']/sale[data['月份'][row[i]]]['Budget 预算']

    return sale


def room_month(filename='hotel data',sheet="月开房情况"):
    path="data/"
    try:
        data = pd.read_excel(path+filename+".xls",sheet_name=sheet,header=0)
    except:
        data = pd.read_excel(path+filename+".xlsx",sheet_name=sheet,header=0)
    
    row=data.index
    num_row=len(row)
    room={}
    for i in range(num_row):
        room[data['月份'][row[i]]]={}
        room[data['月份'][row[i]]]['实际开房数Actual']=data['实际开房数'][row[i]]
        room[data['月份'][row[i]]]['预算开房数Budget']=data['预算开房数'][row[i]]
        room[data['月份'][row[i]]]['Completion Rate预算完成率']=room[data['月份'][row[i]]]['实际开房数Actual']/room[data['月份'][row[i]]]['预算开房数Budget']

    return room

def type_month(filename='hotel data',sheet="住客类型"):
    path="data/"
    try:
        data = pd.read_excel(path+filename+".xls",sheet_name=sheet,header=0)
    except:
        data = pd.read_excel(path+filename+".xlsx",sheet_name=sheet,header=0)
    
    row=data.index
    col=data.columns
    num_row=len(row)
    num_col=len(col)
    jud=data.loc[[2]].isnull()
    for i in range(num_col):
        if jud[col[i]].bool()==True:
            data.drop(col[i],axis=1,inplace=True)
    
    col=data.columns
    num_col=len(col)
    tp_m={}
    label=list(data[col[0]])
    YTD_temp=np.zeros([num_row])
    for i in range(num_col):
        if i==0:
            continue
        tp_m[col[i]]={}
        son_d=list(data[col[i]])
        total=sum(son_d)
        tp_m[col[i]]['total']=total
        for j in range(num_row):
            YTD_temp[j]+=son_d[j]
            tp_m[col[i]][label[j]]=son_d[j]/total
    total=sum(YTD_temp)
    tp_m['YTD']={}
    tp_m['YTD']['total']=total
    for j in range(num_row):
        tp_m['YTD'][label[j]]=YTD_temp[j]/total
            
        
        
    return tp_m


def energy_month(filename='hotel data',sheet="能耗"):
    path="data/"
    try:
        data = pd.read_excel(path+filename+".xls",sheet_name=sheet,header=0)
    except:
        data = pd.read_excel(path+filename+".xlsx",sheet_name=sheet,header=0)
    
    energy_dis={}
    col=data.columns
    num_col=len(col)
    jud=data.loc[[3]].isnull()
    for i in range(num_col):
        if jud[col[i]].bool()==True:
            data.drop(col[i],axis=1,inplace=True)
    dict_receive=dict(list(data.groupby('能耗种类')))
    energy_t=set(list(dict_receive.keys()))
    act={}
    for energy_key in energy_t:
        act[energy_key]={}
        son_data=dict_receive[energy_key].copy()
        son_data.drop('能耗种类',axis=1,inplace=True)
    
        col=son_data.columns
        num_col=len(col)
        row=son_data.index
        num_row=len(row)
        label=list(son_data[col[0]])
        YTD_temp=np.zeros([num_row])
        for i in range(num_col):
            if i==0:
                continue
            act[energy_key][col[i]]={}
            son_d=list(son_data[col[i]])
            total=sum(son_d)
            act[energy_key][col[i]]['合计']=total
            for j in range(num_row):
                YTD_temp[j]+=son_d[j]
                act[energy_key][col[i]][label[j]]=son_d[j]
        total=sum(YTD_temp)
        act[energy_key]['YTD']={}
        act[energy_key]['YTD']['合计']=total
        for j in range(num_row):
            act[energy_key]['YTD'][label[j]]=YTD_temp[j]
    
    save={}
    try:
        b_data = pd.read_excel(path+filename+".xls",sheet_name="能耗预算",header=0)
    except:
        b_data = pd.read_excel(path+filename+".xlsx",sheet_name="能耗预算",header=0)
    
    col=b_data.columns
    num_col=len(col)
    for i in range(num_col):
        if jud[col[i]].bool()==True:
            b_data.drop(col[i],axis=1,inplace=True)
    dict_receive=dict(list(b_data.groupby('能耗种类')))
    energy_t=set(list(dict_receive.keys()))
    b_energy_dis={}
    for energy_key in energy_t:
        b_energy_dis[energy_key]={}
        save[energy_key]={}
        son_data=dict_receive[energy_key].copy()
        son_data.drop('能耗种类',axis=1,inplace=True)
    
        col=son_data.columns
        num_col=len(col)
        row=son_data.index
        num_row=len(row)
        label=list(son_data[col[0]])
        YTD_temp=np.zeros([num_row])
        for i in range(num_col):
            if i==0:
                continue
            b_energy_dis[energy_key][col[i]]={}
            save[energy_key][col[i]]={}
            son_d=list(son_data[col[i]])
            total=sum(son_d)
            b_energy_dis[energy_key][col[i]]['合计']=total
            save[energy_key][col[i]]['合计']=total-act[energy_key][col[i]]['合计']
            for j in range(num_row):
                YTD_temp[j]+=son_d[j]
                b_energy_dis[energy_key][col[i]][label[j]]=son_d[j]
                save[energy_key][col[i]][label[j]]=son_d[j]-act[energy_key][col[i]][label[j]]
        total=sum(YTD_temp)
        b_energy_dis[energy_key]['YTD']={}
        save[energy_key]['YTD']={}
        b_energy_dis[energy_key]['YTD']['合计']=total
        save[energy_key]['YTD']['合计']=total-act[energy_key]['YTD']['合计']
        for j in range(num_row):
            b_energy_dis[energy_key]['YTD'][label[j]]=YTD_temp[j]
            save[energy_key]['YTD'][label[j]]=YTD_temp[j]-act[energy_key]['YTD'][label[j]]
 

    
            
        
    energy_dis['Act']=act
    energy_dis['Budget']=b_energy_dis
    energy_dis['Save']=save
    return energy_dis


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

if __name__ == '__main__':
    sale=jingying_month()
    room=room_month()
    rtype=type_month()
    energy=energy_month()
    hotel={}
    hotel['经营情况']=sale
    hotel['开房情况']=room
    hotel['住客类型']=rtype
    hotel['能耗统计']=energy
    with open('data/hotel.json','w',encoding='utf-8') as f:
        json.dump(hotel,f,indent=1,ensure_ascii=False,cls=NpEncoder)
    f.close()

