# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 10:24:30 2019

@author: Shuo Wan
"""

import os

file_dir='data/'
file_name = os.listdir(file_dir)
xls_list=[]
xlsx_list=[]
for fn in file_name:
    if fn.endswith('.xls'):
        xls_list.append(fn)
    if fn.endswith('.xlsx'):
        xlsx_list.append(fn)

for fxls in xls_list:
    namefxls=fxls.replace('.xls','')
    for fxlsx in xlsx_list:
        namefxlsx=fxlsx.replace('.xlsx','')
        if namefxls==namefxlsx:
            txls=os.path.getmtime(file_dir+fxls)
            txlsx=os.path.getmtime(file_dir+fxlsx)
            if txlsx>txls:
                os.remove(file_dir+fxls)
            else:
                os.remove(file_dir+fxlsx)
                

