#!/usr/bin/env python
#
#   Copyright 2016 Lee Shiueh
#

"""
.. moduleauthor:: Lee Shiueh <lee.shiueh@gmail.com>
twfundclear: A Python module for Taiwan FundClear website data parser
"""

__author__   = 'Lee Shiueh'
__email__    = 'lee.shiueh@gmail.com'
#__url__      = 'https://github.com/pyhys/minimalmodbus'
#__license__  = 'Apache License, Version 2.0'

__version__  = '0.1'
__status__   = 'Beta'

import requests
from requests.adapters import HTTPAdapter

from lxml.html import document_fromstring

from datetime import date
import logging
import sys
import csv, StringIO
import codecs
import json
import shutil
import os

logger = logging.getLogger(__name__)


def fetch_fundcode_csv(save_path=None):
    '''fetch mutual fund code name csv data and 
    write to local file if save_path exist and
    return csv content raw data
    '''
    FUND_CODE_SRC_URL = 'https://announce.fundclear.com.tw/MOPSFundWeb/INQ41SERVLET3?dlType=2&xagentId=all'

    r = requests.get(FUND_CODE_SRC_URL)
    r.raise_for_status()
    
    csv_content = b''
    for chunk in r.iter_content(chunk_size=1024):
        csv_content += chunk
    if save_path:
        with open(save_path,'wb') as fh:
            fh.write(csv_content)
            
    return csv_content

def load_fundcode_csv(csv_file=None):
    '''load and parse fundcode csv file if csv_file exist or
    fetch fundcode from internet,
    return a json object:
    {
        code: {
            code: xxx,
            name_tw: xxx,
            name_en: xxx,
            currency: xxx,
            isincode: xxx,
            distributor_code: xxx,
            distributor_name: xxx
            offshore_fund_institution_code: xxx,
            offshore_fund_institution_name: xxx,
            fund_status: xxx,
        }
        ...
    }
    '''
    if os.path.exists(csv_file): 
        with open(csv_file,'r') as fh:
            csv_text = fh.read()
    else:
        csv_text = fetch_fundcode_csv()
        
    t_lines = csv_text.split('\n')
    t_header = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,' % ('code',
                                                     'name_tw',
                                                     'name_en',
                                                     'currency',
                                                     'isincode',
                                                     'distributor_code',
                                                     'distributor_name',
                                                     'institution_code',
                                                     'institution_name',
                                                     'fund_status')
    t_lines[0] = t_header
    t_content = '\n'.join(t_lines)
    csv_reader = csv.DictReader(StringIO.StringIO(t_content))
    codename_dict = {}
    for row in csv_reader:
        t_fund_meta = dict(row)
        t_fund_meta.pop('')
        t_fund_meta['code'] = t_fund_meta['code'].replace('=','').replace('"','')
        t_fund_meta['name_tw'] = codecs.decode(t_fund_meta['name_tw'],'big5' )
        t_fund_meta['distributor_name'] = codecs.decode(t_fund_meta['distributor_name'],'big5' )
        t_fund_meta['institution_name'] = codecs.decode(t_fund_meta['institution_name'],'big5' )
        t_fund_meta['institution_code'] = t_fund_meta['institution_code'].replace('=','').replace('"','')
        t_fund_meta['isincode'] = t_fund_meta['isincode'].replace('=','').replace('"','')
        
        codename_dict[t_fund_meta['code']] = t_fund_meta
    return codename_dict

def test_fundcode():
    filename = 'fund_codename_%s' % date.today().strftime('%Y%m%d')
    fetch_fundcode_csv(filename)
    fundcode = load_fundcode_csv(filename)
    count = 1
    for t_code in fundcode:
        sys.stdout.write('%s\n' % json.dumps(fundcode[t_code],indent=2,encoding="big5"))
        count += 1
        if count > 10:
            break

def fetch_fundnav_html(fund_code, year, save_path=None):
    '''fetch mutual fund nav for specific year and 
    write to a local file if save_path provided
    return fetched html content
    '''
    
    FUND_NAV_SRC_URL_TEMPLATE = 'https://announce.fundclear.com.tw/MOPSFundWeb/D02_02P.jsp?fundId={fund_id}&beginDate={begin_date}&endDate={end_date}'

    begin_date = date(int(year),1,1).strftime("%Y/%m/%d")
    if int(year) == date.today().year:
        end_date = date.today().strftime("%Y/%m/%d")
    else:
        end_date = date(int(year),12,31).strftime("%Y/%m/%d")  
    url = FUND_NAV_SRC_URL_TEMPLATE.format(fund_id=fund_code,
                              begin_date=begin_date,
                              end_date=end_date)
    sys.stdout.write('%s\n' % url)
    r = requests.get(url)
    r.raise_for_status()
    html_content = b''
    for chunk in r.iter_content(chunk_size=1024):
        html_content += chunk

    if save_path:
        with open(save_path,'wb') as fh:
            fh.write(html_content)
    
    return html_content
    
def load_fundnav_html(save_path):
    '''load and parse fundnav_{fundcode}_{yyyy}.html and 
    return a json object:
    [
        [{yyyy-MM-dd}, {nav-value}], 
        ...
    ]    
    '''
    html_content = None
    with open(save_path,'rb') as fh:
        html_content = fh.read()

    html_content = document_fromstring(codecs.decode(html_content,'big5','ignore'))
    t_tables = html_content.xpath("//table")
    TABLE_TITLE_INDEX = 4
    TABLE_NAV_INDEX_START = 5
    fund_title = t_tables[TABLE_TITLE_INDEX][0][0].text.replace('\r\n','')
    t_total = len(t_tables)
    #logging.debug('t_total: ' + str(t_total))
    t_count = TABLE_NAV_INDEX_START
    dataset = []
    
    while (t_count <= (t_total-1)):
        if len(t_tables[t_count]) == 2:
            t_date_list = [t_child.text for t_child in t_tables[t_count][0]]
            t_value_list = [t_child.text for t_child in t_tables[t_count][1]]
            for i in range(0,len(t_date_list)):
                if i != 0:
                    if (t_date_list[i].strip() != ''):
                        dataset.append([t_date_list[i],t_value_list[i]])
                    #else:
                    #    logging.debug('remove element ('+ str(t_count) + '#' + str(i) + '): ' + str([t_date_list[i],t_value_list[i]]))
        #else:
        #    logging.debug('skip table:\n' + etree.tostring(t_tables[t_count]))
        t_count += 1
    
    fund_nav = []
    t_count = 0
    while (t_count < len(dataset)):
        #logging.info('t_count ' + str(t_count))
        (_,t_value) = dataset[t_count]
        #logging.debug(str(t_count) + ' ' + str(dataset[t_count]))
        if (t_value == '--') or (t_value == 'N/A') or (t_value == '.000000'):
            del dataset[t_count]
            continue
        fund_nav.append([dataset[t_count][0],float(dataset[t_count][1])])
        t_count += 1

    return (fund_title,fund_nav)
    
def test_fundnav(step=1):
    
    fund_us_stock = 'LU0048573561'
    fund_energy = 'AXAWFJEUSD'
    
    fund_code = fund_energy
    year = date.today().year
    save_path = '%s_%s.html' % (fund_code, year)
    if step == 1:
        retry_count = 0
        while (retry_count <= 2):
            try:
                fetch_fundnav_html(fund_code, year, save_path)
                break
            except requests.exceptions.ConnectionError:
                retry_count += 1
                sys.stdout.write('retry count %d\n' % retry_count)
    else:
        _,fundnav = load_fundnav_html(save_path)
        count = 1
        for entry in fundnav:
            sys.stdout.write('%s\n' % str(entry))
            count += 1
            if count > 31:
                break

def post_fundnav_html(fund_code, year, post_url):
    '''fetch fundnav from fundclear website (and save as a local file)
    and post the html content to post_url with post key post_arg_name
    '''
    tmp_html_filename = '%s_%s.html' % (fund_code,year)
    retry_count = 0
    while (retry_count <= 2):
        try:
            web_html = fetch_fundnav_html(fund_code, year, save_path=tmp_html_filename)
            break
        except requests.exceptions.ConnectionError:
            retry_count += 1
            sys.stdout.write('fetch retry %d\n' % retry_count)
    
    sys.stdout.write('post\n')
    fund_title, csv_content = load_fundnav_html(tmp_html_filename)
    sys.stdout.write('%s\n' % fund_title)    
    data = { 'fund_title': fund_title,
            'csv_content': csv_content}
    r = requests.post(post_url,data = data)
    with open('pose_raw_response.html', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)    
    return r.text
    
def test_post_fundnav_html(fund_id=None, fetch_year=None):
    
    post_url = 'https://trusty-catbird-645.appspot.com/fc2/view/json/{p_fund_id}/{p_year}/'
    fund_us_stock = 'LU0048573561'
    fund_energy = 'AXAWFJEUSD'
    fund_japan = 'LU0997587166'
    
    if fund_id is None:
        fund_code = fund_japan
    else:
        fund_code = fund_id
    if fetch_year is None:
        year = date.today().year
    else:
        year = fetch_year
        
    post_url = post_url.format(p_fund_id = fund_code,
                               p_year = year)
    sys.stdout.write('%s\n' % post_url)
    response_text = post_fundnav_html(fund_code, year, post_url)
    sys.stdout.write(response_text)
                
if __name__ == '__main__':
    #test_fundnav(1)
    #test_fundnav(2)
    if sys.argv[1] is None or sys.argv[2] is None:
        test_post_fundnav_html()
    else:
        test_post_fundnav_html(sys.argv[1],sys.argv[2])
    
    
    
    
    
    