
import requests

from lxml.html import document_fromstring

from datetime import date
import logging
import sys
import codecs
import os
from retrying import retry

logger = logging.getLogger(__name__)

FUND_NAV_SRC_URL_TEMPLATE = 'https://announce.fundclear.com.tw/MOPSFundWeb/D02_02P.jsp?fundId={fund_id}&beginDate={begin_date}&endDate={end_date}'
FUND_NAV_HTML_ROOL = os.path.join(os.path.dirname(__file__),'data')

def get_fundnav_filepath(fund_code,year):
    '''Return the default download save file path for Fund NAV HTML page
        ./data/<fund_code>/<fund_code>_<year>.html
    '''
    fund_nav_html_dirname = os.path.join(FUND_NAV_HTML_ROOL,fund_code)
    if not os.path.exists(fund_nav_html_dirname):
        os.makedirs(fund_nav_html_dirname)
    filename = '%s_%s.html' % (fund_code,year)
    fund_nav_html_file = os.path.join(fund_nav_html_dirname,filename)
    return fund_nav_html_file

@retry(stop_max_attempt_number=3,wait_fixed=1000)
def download_fundnav_html(fund_code, year):
    '''Download and save TW FundClear Fund NAV HTML page
    and return HTML content if download success
    '''
    logger.debug('download_fundnav_html(%s,%s)' % (fund_code,year))
    begin_date = date(int(year),1,1).strftime("%Y/%m/%d")
    if int(year) == date.today().year:
        end_date = date.today().strftime("%Y/%m/%d")
    else:
        end_date = date(int(year),12,31).strftime("%Y/%m/%d")  
    url = FUND_NAV_SRC_URL_TEMPLATE.format(fund_id=fund_code,
                              begin_date=begin_date,
                              end_date=end_date)
    logger.debug('fund nav url: %s' % url)
    
    r = requests.get(url)
    r.raise_for_status()
    html_content = b''
    for chunk in r.iter_content(chunk_size=1024):
        html_content += chunk
    
    fund_nav_html_file = get_fundnav_filepath(fund_code,year)
    with open(fund_nav_html_file,'wb') as fh:
        fh.write(html_content)
    
    return html_content
    
def load_fundnav(fund_code,year):
    '''load and parse Fund NAV from downloaded HTML file 
    and return a Dict object:
        [
            [{yyyy-MM-dd}, {nav-value}], 
            ...
        ]    
    '''
    save_path = get_fundnav_filepath(fund_code, year)
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
