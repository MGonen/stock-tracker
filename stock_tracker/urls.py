
from django.conf.urls import url

import views

urlpatterns = (
    url(r'^$', views.Main.as_view(), name='main'),
    url(r'^results/(?P<symbol>[\w\.-]+)/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})/$', views.results_details, name='results_details'),
    # url(r'^results/(?P<start_date>\d{4}-\d{2}-\d{2})/$', views.results_details_date, name='results_details'),
    # url(r'^results/(?P<symbol>[\w\.]+)/(?P<start_date>\d{4}-\d{2}-\d{2})/$', views.results_details_symbol_date, name='result_details_symbol')
)
