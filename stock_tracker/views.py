# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views.generic import View
from django.utils.dateparse import parse_date
from django.urls import reverse

from jsonview.decorators import json_view
import datetime

from .forms import MainForm
from .models import Company, Stock
from .utils import GetResults


# Create your views here.


# Filling Company DB
class Main(View):
    template_name = 'stock_tracker/main.html'

    def get_results(self, form):
        percentage = form['increase_percentage'].value()
        min_volume = form['minimum_volume'].value()
        max_volume = form['maximum_volume'].value()
        start_date = form['start_date'].value()
        end_date = form['end_date'].value()

        return GetResults.main(percentage, min_volume, max_volume, start_date, end_date)

    def get(self, request):
        today = datetime.datetime.today()
        end_date = today - datetime.timedelta(days=today.weekday()) - datetime.timedelta(7)
        formatted_end_date = end_date.strftime('%Y-%m-%d')
        start_date = end_date - datetime.timedelta(91)
        formatted_start_date = start_date.strftime('%Y-%m-%d')

        form = MainForm(initial={'increase_percentage':'10', 'minimum_volume': '1', 'maximum_volume':1000, 'start_date': formatted_start_date, 'end_date': formatted_end_date})
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        print 'RETRIEVING DATA'
        form = MainForm(request.POST)
        if form.is_valid():
            # results = self.get_results_alt(form)
            results = self.get_results(form)
            print 'results:', len(results)
            return render(request, self.template_name, {'form': form, 'results': results})


def get_result_details(symbol, start_date, end_date):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    results = []
    company_stocks = list(
        Stock.objects.filter(company__symbol=symbol, date__gte=start_date, date__lte=end_date).order_by('date'))
    increase_percentage = round(100 * (company_stocks[-1].price - company_stocks[0].price) / company_stocks[0].price, 2)

    for stock in company_stocks:
        results.append({'date': stock.date, 'price': stock.price, 'volume': stock.volume * stock.price})

    company = Company.objects.get(symbol=symbol)

    return {'company_name': company.name, 'exchange': company.exchange, 'country': company.country,  'increase': increase_percentage, 'results': results}



def results_details(request, symbol, start_date, end_date):
    return render(request, 'stock_tracker/results_details.html', get_result_details(symbol, start_date, end_date))





        # Getting Stock Info per Day
def get_stock_info(request):
    # GetStockInfo.main()
    return redirect('admin:index')


