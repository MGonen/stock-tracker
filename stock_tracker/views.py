# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views.generic import View
from django.utils.dateparse import parse_date
from django.urls import reverse
from django.http import HttpResponse

from jsonview.decorators import json_view
import datetime
import csv

from .forms import MainForm
from .models import Company, Stock
from .utils import GetResults


# Create your views here.


# Filling Company DB
class Main(View):
    template_name = 'stock_tracker/main.html'

    def convert_date(self, date):
        return '%s-%s-%s' % (date[8:10], date[5:7], date[0:4])

    def get_results(self, form):
        min_percentage = form['min_percentage_increase'].value()
        max_percentage = form['max_percentage_increase'].value()
        min_volume = form['minimum_volume'].value()
        max_volume = form['maximum_volume'].value()
        start_date = form['start_date'].value()
        end_date = form['end_date'].value()

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Companies %s - %s.csv"' % (start_date, end_date)

        writer = csv.writer(response, delimiter=str(';'), dialect='excel')

        extra_content = [
            ['', 'From:', self.convert_date(start_date)],
            ['', 'To:', self.convert_date(end_date)],
            ['', 'Minimum Percentage increase:', min_percentage],
            ['', 'Maximum Percentage increase:', max_percentage],
            ['', 'Minimum Turnover Volume (in millions):', float(min_volume)],
            ['', 'Maximum Turnover Volume (in millions):', float(max_volume)],
        ]

        writer.writerow([''])
        writer.writerow(['COMPANY', 'EXCHANGE', 'COUNTRY', 'INCREASE PERCENTAGE', 'START PRICE', 'END PRICE', 'TURNOVER VOLUME', 'START DATE', 'END DATE'])

        i = -1
        for result in GetResults.main(min_percentage, max_percentage, min_volume, max_volume, start_date, end_date):
            if result:
                i += 1
                try:
                    if i < len(extra_content):
                        result += extra_content[i]
                    writer.writerow(result)
                except:
                    continue

        return response

    def get(self, request):
        today = datetime.datetime.today()
        end_date = today - datetime.timedelta(days=today.weekday()) - datetime.timedelta(6)
        formatted_end_date = end_date.strftime('%Y-%m-%d')
        start_date = end_date - datetime.timedelta(91)
        formatted_start_date = start_date.strftime('%Y-%m-%d')

        form = MainForm(initial={"min_percentage_increase": '10', 'max_percentage': '20', 'minimum_volume': '1', 'maximum_volume':1000, 'start_date': formatted_start_date, 'end_date': formatted_end_date})
        return render(request, self.template_name, {'form': form})

    # def post(self, request):
    #     print 'RETRIEVING DATA'
    #     form = MainForm(request.POST)
    #     if form.is_valid():
    #         # results = self.get_results_alt(form)
    #         results = self.get_results(form)
    #         print 'results:', len(results)
    #         return render(request, self.template_name, {'form': form, 'results': results})

    def post(self, request):
        form = MainForm(request.POST)
        if form.is_valid():
            return self.get_results(form)


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


