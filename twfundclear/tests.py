from django.test import TestCase
import fundcode, fundnav
import os
import random
from datetime import datetime

# Create your tests here.

class FundCodeTestCase(TestCase):
    
    def test_download_csv_file(self):
        csv_content = fundcode.download_csv_file()
        self.assertTrue(os.path.exists(fundcode.FUND_CODE_CSV_FILE_PATH), 
                        'The file FUND_CODE_CSV_FILE_PATH should be created after downloaded')
        self.assertTrue(len(csv_content) > 0, 'The CSV content should not be empty.')
    
    
    def test_load_fundcode(self):
        self.assertTrue(os.path.exists(fundcode.FUND_CODE_CSV_FILE_PATH),
                        'The FundCode CSV file should be downloaded first.')
        
        dict_content = fundcode.load_fundcode()
        
        self.assertTrue(len(dict_content.keys()) > 0, 'The FundCode Dict object should have multiple keys.')
        self.assertTrue(len(dict_content) > 0, 'There should multiple entry in FundCode Dict object.')

class FundNavTestCase(TestCase):
    
    def setUp(self):
        self.year = datetime.now().year
        self.fundcode = fundcode.load_fundcode()
        self.fund_code = self.fundcode.items()[-int(random.random() * len(self.fundcode))][1]['code']
         
    def test(self):
        fundnav.download_fundnav_html(self.fund_code, self.year)