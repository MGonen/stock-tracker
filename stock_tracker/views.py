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


# Create your views here.


# Filling Company DB
class Main(View):
    template_name = 'stock_tracker/main.html'


    def get_results(self, form):
        print 'GETTING RESULTS'
        start_time = datetime.datetime.now().replace(microsecond=0)
        results = []

        for company in Company.objects.all():
            results.append(self.get_one_result(company, form))

        results = filter(None, results)
        end_time = datetime.datetime.now().replace(microsecond=0)
        print 'total time:', end_time - start_time
        return results


    def get_one_result(self, company, form):
        required_increase_percentage = float(form['increase_percentage'].value())
        minimum_volume = float(form['minimum_volume'].value()) * 1000000
        start_date = form['start_date'].value()
        end_date = form['end_date'].value()

        company_stocks = Stock.objects.filter(company=company)
        start_date_stock = self.get_closest_date_stock(company_stocks, start_date)
        end_date_stock = self.get_closest_date_stock(company_stocks, end_date)

        # print '\ncompany:', company.name

        if not start_date_stock or not end_date_stock:
            # print 'Missing one of the dates'
            return

        if start_date_stock.price == 0:
            increase_percentage = 0
        else:
            increase_percentage = round(100*(end_date_stock.price - start_date_stock.price)/start_date_stock.price,2)

        if abs(increase_percentage) <= required_increase_percentage:
            # print 'Price difference not big enough:', abs(increase_percentage), required_increase_percentage, abs(increase_percentage) < required_increase_percentage
            return

        if start_date_stock.volume * start_date_stock.price < minimum_volume or end_date_stock.volume * start_date_stock.price < minimum_volume:
            # print 'Turn over not big enough'
            return

        volume = end_date_stock.volume * end_date_stock.price
        return {'symbol': company.symbol, 'exchange': end_date_stock.company.exchange, 'country': end_date_stock.company.country, 'increase': increase_percentage, 'start_price':start_date_stock.price, 'end_price': end_date_stock.price, 'volume': volume}


    def get_closest_date_stock(self, stocks, date):
        if not stocks:
            return

        date = parse_date(date)
        if stocks.filter(date=date).exists():
            return stocks.get(date=date)

        else:
            gte_stocks = stocks.filter(date__gte=date).order_by('date')
            lte_stocks = stocks.filter(date__lte=date).order_by('-date')

            if gte_stocks:
                closest_gt_stock = gte_stocks[0]
                dif_gt_stock = abs(closest_gt_stock.date - date).days
            else:
                dif_gt_stock = 10


            if lte_stocks:
                closest_lt_stock = lte_stocks[0]
                dif_lt_stock = abs(closest_lt_stock.date - date).days
            else:
                dif_lt_stock = 10

            if dif_gt_stock > 7 and dif_lt_stock > 7:
                return

            elif dif_gt_stock > dif_lt_stock:
                return closest_lt_stock

            return closest_gt_stock




    def get(self, request):
        form = MainForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        print 'RETRIEVING DATA'
        form = MainForm(request.POST)
        if form.is_valid():

            return render(request, self.template_name, {'form': form, 'results': self.get_results(form)})


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


