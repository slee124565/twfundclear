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

def fetch_fundnav_html(year):
    '''fetch mutual fund nav for specific year and write to a local file
    with filename fundnav_{fundcode}_{yyyy}.html
    '''
    pass
    
def load_fundnav_html(year):
    '''load and parse fundnav_{fundcode}_{yyyy}.html and 
    return a json object:
    [
        [{yyyy-MM-dd}, {nav-value}], 
        ...
    ]    
    '''
    pass


if __name__ == '__main__':
    filename = 'fund_codename_%s' % date.today().strftime('%Y%m%d')
    fetch_fundcode_csv(filename)
    fundcode = load_fundcode_csv(filename)
    count = 1
    for t_code in fundcode:
        sys.stdout.write('%s\n' % json.dumps(fundcode[t_code],indent=2,encoding="big5"))
        count += 1
        if count > 10:
            break
