from django.views.generic import View
from django.http import HttpResponse

class FundNavBollingerBand(View):
    ''''''
    
    def get(self, request, *args, **kwargs):
        fund_code = self.kwargs.get('fund_code')
        return HttpResponse('Hello with Fund Code %s!' % fund_code)