from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from twfundclear import fundcode, fundnav
from math_util import bollingerband

import json
import logging
logger = logging.getLogger(__name__)

class MyFundListApi(View):

    def get(self, request, *args, **kwargs):
        code_list = settings.MY_FUND_CODE_LIST
        fund_list_all = fundcode.load_fundcode()
        fund_list = {}
        for code in code_list:
            fund_meta = fund_list_all.get(code,None)
            if fund_meta is None:
                logger.warning('Fund Code %s Not Found' % code)
            else:
                logger.debug('Fund Code %s with name %s %s' % (
                                                               code,fund_meta['name_en'],fund_meta['name_tw']))
                fund_list[code] = fund_meta
        return JsonResponse(fund_list)
    
class FundBBDataApi(View):

    def get(self, request, *args, **kwargs):
        fund_code = kwargs.get('fund_code',None)
        if fund_code is None:
            logger.warning('Fund Code %s Not Found' % fund_code)
        else:
            fund_nav = fundnav.load_from_json(fund_code)
#             bollingerband.get_bollinger_band(date_value_list, sample_size, std_weight)
            
        return HttpResponse('TODO: FundBBDataApi for Fund %s' % fund_code)

    