# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 01:47:40 2018

@author: yinchao
"""
import sys
sys.path.append('../..')

from datetime import datetime
import crawling_finance_table
import crawling_finance_table_v1_7
import pymysql
import os
def Connect_sql(account):
    conn = pymysql.connect(
            host = account[0].strip(),
            port = 3306,
            user = account[1].strip(),
            passwd = account[2].strip(),
            db = account[3].strip(),
            charset = "utf8"
            )
    
    cur = conn.cursor()
    print("\nconnect to aliyun success!\n")
    return cur





parameter = [
 '总资产',
 '净资产',
 '资产负债比',
 '流动资产',
 '一年内到期的长期负债',
 '应收账款',
 '预收账款',
 '存货',
 '营业收入',
 '营业成本',
 '营业税金及附加',
 '财务费用',
 '营业外收入',
 '净利润',
 '除非净利润',
 '每股收益',
 '经营净额',
 '投资净额',
 '筹资净额',
 '汇率影响',
 '现金净增加额',
 '期末现金余额',
 '流动比率',
 '资产周转率',
 '存货周转率',
 '溢价比',
 '市盈率',
 '市净率',
 '名义净资产收益率',
 '真实净资产收益率',
 '毛利率',
 '营收增长率',
 '除非净利润增长率',
 '股息率',
 '分红率']

id_list = ['000651', '000333', '600690'] #此处可以修改
global data_base_path
data_base_path = '../history_data/'
def M1809_local_config(company_list):
    '''
    本地模式配置
    只需要提供感兴趣的对比公司即可，如果只有一个，说明只进行自主分析
    '''
    global data_base_path
    print('please wait, check for updating...')
    for item in company_list:

        
        try:
            file_name = data_base_path + item + '_profit.csv'
#            print(file_name)
            with open(file_name, 'r') as fh:
                from datetime import datetime
                from dateutil.parser import parse
                from dateutil.relativedelta import relativedelta
                content = fh.readlines()
                s = content[-1].split(',')
                latest_record = parse(s[0]) #获取最新时间
                
                current_day = datetime.now() - relativedelta(months=+12) 
#                print(latest_record)
#                print(current_day)
                if latest_record > current_day:
                    pass
                else:
                    cbfx = crawling_finance_table_v1_7.crawling_finance(path,item)
                    cbfx.crawling_update()                    
        except:
            cbfx = crawling_finance_table_v1_7.crawling_finance(path,item)
            cbfx.crawling_update()  
        
    print('finished!')
    return parameter, company_list
    
    
def M1809_config():
    '''
    网络模式配置
    以读文件的方式获取配置参数
    1. 读取待考察的参数
    2. 读取公司名称列表，并转换成id（如果输入无法解析成id，会自动剔除）
    3. 更新该公司的财务报表，以备以后使用
    注意：文件名不可改
    '''
    del parameter[:]
    with open ('./config/parameter_list.txt','r',encoding = 'utf-8') as fh:
        ct = fh.readlines()
    
    
    for s in ct:
        items = s.strip()
        if items != '': 
            if items[0] == '#': #剔除注释部分
                break
            parameter.append(items)
    
    del id_list[:]
    with open('./config/company_list.txt','r', encoding = 'utf-8') as fh:
        ct = fh.readlines()
    company = []
    for s in ct:
        if s.strip() != '': 
            company.append(s.strip())
    try:
        with open('./config/account.txt', 'r') as fh:
            account = fh.readlines()
    except:
        print('fail to initialize.')
        return
    cur = Connect_sql(account)
    for name in company:
        cmd = "select * from anack_classify where name = \'"+name+"\';"
        cur.execute(cmd)
        result = cur.fetchall()
        try:
            id = result[0][0] 
            id_list.append(id)
            
        except: #错误的ID号不会被解析（刚上市的，不会出现在anack_classify里，需要更新）
            print(name+' is not in list')
            pass   
    try:
        os.mkdir('.//output')
    except:
        pass 
#    print(id_list)
    M1809_Update(cur, id_list)
    return cur, parameter, id_list


def M1809_Update(cur, id_list):
    '''
    更新数据库
    '''
    print('check for update,please wait...')
    print(id_list)
    for item in id_list:
        cmd = "select * from zichanfuzai where h79 = \'" + item + "\' and h80 = \'" + str(datetime.now().year - 1)+"-12-31\';"
        cur.execute(cmd)
        result = cur.fetchall()
        cmd2 = "select * from cashFlow where h72 = \'" + item + "\' and h73 = \'" + str(datetime.now().year - 1)+"-12-31\';"
        cur.execute(cmd2)
        result2 = cur.fetchall()
        cmd3 = "select * from Profit where h29 = \'" + item + "\' and h30 = \'" + str(datetime.now().year - 1)+"-12-31\';"
        cur.execute(cmd3)
        result3 = cur.fetchall()
        try:
            trash_data = result[0] #获得资产负债表信息
            trash_data = result2[0] #获得资产负债表信息
            trash_data = result3[0] #获得资产负债表信息
            print('here')
        except:
            print('updating ', item)
            cbfx = crawling_finance_table.crawling_finance('',item,'')
            cbfx.crawling_update()
    print('update check finished!') 

#############################################################################
if __name__ =='__main__':
    #网络测试
#    cur, para,list_id = M1809_config()     
    
    #本地测试
    para, company = M1809_local_config(id_list)
        