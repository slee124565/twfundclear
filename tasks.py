
fund_code_list = [
                  'LU0048573561',
                  'AXAWFJEUSD',
                  'LU0346390866',
                  'LU0197229882',
                  'IUKEG',
                  'LU0823431563',
                  'LU0050427557',
                  'LU0997587166',
                  'LU1046421878',
                  ]

import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()

from twfundclear import fundnav

def storage_init():
    for fund_code in fund_code_list:
        fundnav.file_storage_initialize(fund_code)

def storage_update():
    for fund_code in fund_code_list:
        fundnav.file_storage_update(fund_code)
    
if __name__ == '__main__':
    #storage_init()
    storage_update()