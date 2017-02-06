import requests
import logging
import os
import csv, StringIO
import codecs
from retrying import retry

logger = logging.getLogger(__name__)

FUND_CODE_CSV_SRC_URL = 'https://announce.fundclear.com.tw/MOPSFundWeb/INQ41SERVLET3?dlType=2&xagentId=all'
#FUND_CODE_CSV_SRC_URL = 'https://announce.fundclear.com.tw/MOPSFundWeb/INQ41SERVLET3'
FUND_CODE_CSV_FILE_PATH = os.path.join(os.path.dirname(__file__),'data','fundcode.csv')

@retry(stop_max_attempt_number=3,wait_fixed=1000)
def download_csv_file():
    '''Download TW FundCode CSV file and save as ./data/fundcode.csv.
    The CSV file content will be return'''
    
#     params = {'dlType': 2,'xagentId':'all'}
#     headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    #r = requests.get(FUND_CODE_CSV_SRC_URL,params=params)
    #r = requests.post(FUND_CODE_CSV_SRC_URL,data=params,headers=headers)
    r = requests.get(FUND_CODE_CSV_SRC_URL)
    r.raise_for_status()
    
    csv_content = b''
    for chunk in r.iter_content(chunk_size=1024):
        csv_content += chunk
        logger.debug('fundcode csv fetch chunk len %d' % len(chunk))

    save_path = FUND_CODE_CSV_FILE_PATH
    with open(save_path,'wb') as fh:
        fh.write(csv_content)
            
    return csv_content

def load_fundcode():
    '''load and parse TW FundCode CSV file and return a Dict object
    
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
    
    if not os.path.exists(FUND_CODE_CSV_FILE_PATH): 
        raise Exception('TW FundCode CSV file not exist.')
    
    with open(FUND_CODE_CSV_FILE_PATH,'r') as fh:
        csv_text = fh.read()
        
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

