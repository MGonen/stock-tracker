# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views.generic import View
from django.utils.dateparse import parse_date
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from jsonview.decorators import json_view
import datetime

from .forms import MainForm
from .models import Company, Stock


# Create your views here.


# Filling Company DB
class Main(View):
    template_name = 'stock_tracker/main.html'


    def get_results(self, post_request):
        percentage = post_request.get('percentage')
        volume = post_request.get('volume')
        start_date = post_request.get('startDate')
        end_date = post_request.get('endDate')

        print '\n', percentage, volume, start_date, end_date, '\n'

        results = []
        start_time = datetime.datetime.now().replace(microsecond=0)
        chunks = 278
        for i in range(chunks):
            start_index = i* 100
            end_index = (i+1) * 100
            results += GetResults.main(percentage, volume, start_date, end_date, start_index, end_index)
        end_time = datetime.datetime.now().replace(microsecond=0)
        print 'total time: %s seconds' % (end_time - start_time)

        return results


    def get(self, request):
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        return render(request, self.template_name, {'today':today})

    def post(self, request):
        return render(request, self.template_name, {'results': self.get_results(request.POST)})


class GetResults():

    @classmethod
    def main(cls, percentage, volume, start_date, end_date, start_index, end_index): #, from_company_number, to_company_number
        percentage = float(percentage)
        volume = float(volume)
        print 'GETTING CHUNK RESULTS. '
        # print 'All values:', percentage, volume, start_date, end_date, start_index, end_index
        results = []
        for company in Company.objects.all()[start_index:end_index]:
            results.append(cls.get_one_result(company, percentage, volume, start_date, end_date))

        results = filter(None, results)
        print 'FINISHED CHUNK. Number of results:', len(results)
        return results

    @classmethod
    def get_one_result(cls, company, percentage, volume, start_date, end_date):
        company_stocks = Stock.objects.filter(company=company)
        start_date_stock = cls.get_closest_date_stock(company_stocks, start_date)
        end_date_stock = cls.get_closest_date_stock(company_stocks, end_date)

        # print '\ncompany:', company.name

        if not start_date_stock or not end_date_stock:
            # print 'Missing one of the dates'
            return

        if start_date_stock.price == 0:
            increase_percentage = 0
        else:
            increase_percentage = round(100*(end_date_stock.price - start_date_stock.price)/start_date_stock.price,2)

        if abs(increase_percentage) <= percentage:
            # print 'Price difference not big enough:', abs(increase_percentage), required_increase_percentage, abs(increase_percentage) < required_increase_percentage
            return

        if start_date_stock.volume * start_date_stock.price < volume * 1000000 or end_date_stock.volume * start_date_stock.price < volume * 1000000:
            # print 'Turn over not big enough'
            return

        volume = end_date_stock.volume * end_date_stock.price
        return {'symbol': company.symbol, 'exchange': end_date_stock.company.exchange, 'country': end_date_stock.company.country, 'increase': increase_percentage, 'start_price':start_date_stock.price, 'end_price': end_date_stock.price, 'volume': volume}

    @classmethod
    def get_closest_date_stock(cls, stocks, date):
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

@csrf_exempt
@json_view
def get_search_results(request):
    # print 'request.POST:', request.POST
    percentage = request.POST.get('percentage')
    volume = int(request.POST.get('volume'))
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    i = int(request.POST.get('i'))
    start_index = 100 * i
    end_index = 100 * (i + 1)

    # print '\n\npercentage: %s\nvolume: %s\nstartDate: %s\nendDate: %s\nstart index: %s\nEnd Index: %s\n\n' % (percentage, volume, start_date, end_date, start_index, end_index)
    results = GetResults.main(percentage, volume, start_date, end_date, start_index, end_index)
    return results


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


