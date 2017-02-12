from django.views.generic import View
# from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

class ModuleDefaultView(View):
    
    def get(self, request, *args, **kwargs):
        return HttpResponse('twfundclear Default View')
    
class FundCodeApiView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('twfundclear.fundcode api View')
    
class FundNavApiView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('twfundclear.fundnav api View')
        