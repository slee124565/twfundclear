
from django.conf.urls import url
from .views import ModuleDefaultView, FundCodeApiView, FundNavApiView

urlpatterns = [
    
    url(r'^api/code$', FundCodeApiView.as_view() ,name='TwFundCodeApi'),
    url(r'^api/nav$', FundNavApiView.as_view() ,name='TwFundNavApi'),

    url(r'^$', ModuleDefaultView.as_view() ,name='TwFundClear'),
    
]
