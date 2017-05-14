# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views.generic import View
from django.utils.dateparse import parse_date
from django.urls import reverse
from django.db.models import Q

from jsonview.decorators import json_view
import datetime

from .forms import MainForm
from .models import Company, Stock


# Create your views here.


# Filling Company DB
class Main(View):
    template_name = 'stock_tracker/main.html'


    def get_results_alt(self, form):
        percentage = float(form['increase_percentage'].value())
        min_volume = int(form['minimum_volume'].value()) * 1000000
        max_volume = int(form['maximum_volume'].value()) * 1000000
        start_date = form['start_date'].value()
        end_date = form['end_date'].value()

        whitelist_countries = [
            u'Australia',
            u'Austria',
            u'Belgium',
            u'Canada',
            u'Denmark',
            u'Finland',
            u'France',
            u'Germany',
            u'Greece',
            u'Hong Kong',
            u'Iceland',
            u'India',
            u'International',
            u'Italy',
            u'Korea',
            u'Latvia',
            u'Lithuania',
            u'Netherlands',
            u'New Zealand',
            u'Norway',
            u'Portugal',
            u'Singapore',
            u'South Korea',
            u'Spain',
            u'Sweden',
            u'Taiwan',
            u'UK',
            u'USA',
        ]

        date_filtered_stocks = Stock.objects.filter(Q(date=start_date) | Q(date=end_date)).order_by('company', 'date')
        filtered_stocks = date_filtered_stocks.filter(company__country__in=whitelist_countries)

        results = []

        for i in range(len(filtered_stocks)-1):
            # print '%s/%s' % (i, len(filtered_stocks))
            if filtered_stocks[i].company != filtered_stocks[i+1].company:
                continue

            else:
                start_date_stock = filtered_stocks[i]
                end_date_stock = filtered_stocks[i + 1]

            if not start_date_stock or not end_date_stock:
                # print 'Missing one of the dates'
                continue

            if start_date_stock.price == 0:
                increase_percentage = 0
            else:
                increase_percentage = round(100*(end_date_stock.price - start_date_stock.price)/start_date_stock.price,2)

            if abs(increase_percentage) <= percentage:
                # print 'Price difference not big enough:', abs(increase_percentage), required_increase_percentage, abs(increase_percentage) < required_increase_percentage
                continue


            if not (max_volume > start_date_stock.volume * start_date_stock.price > min_volume or max_volume > end_date_stock.volume * end_date_stock.price > min_volume):
                # print 'Turn over not big enough',
                continue

            results.append({
                'symbol': start_date_stock.company.symbol,
                'exchange': end_date_stock.company.exchange,
                'country': end_date_stock.company.country,
                'increase': increase_percentage,
                'start_price':start_date_stock.price,
                'end_price': end_date_stock.price,
                'volume': end_date_stock.volume * end_date_stock.price
            })

        return results

    def get_results(self, form):
        percentage = float(form['increase_percentage'].value())
        min_volume = int(form['minimum_volume'].value()) * 1000000
        max_volume = int(form['maximum_volume'].value()) * 1000000
        start_date = form['start_date'].value()
        end_date = form['end_date'].value()

        whitelist_countries = [
            u'Australia',
            u'Austria',
            u'Belgium',
            u'Canada',
            u'Denmark',
            u'Finland',
            u'France',
            u'Germany',
            u'Greece',
            u'Hong Kong',
            u'Iceland',
            u'India',
            u'International',
            u'Italy',
            u'Korea',
            u'Latvia',
            u'Lithuania',
            u'Netherlands',
            u'New Zealand',
            u'Norway',
            u'Portugal',
            u'Singapore',
            u'South Korea',
            u'Spain',
            u'Sweden',
            u'Taiwan',
            u'UK',
            u'USA',
        ]

        date_filtered_stocks = Stock.objects.filter(Q(date=start_date) | Q(date=end_date)).order_by('company', 'date')
        filtered_stocks = date_filtered_stocks.filter(company__country__in=whitelist_countries)

        results = []

        i = -1
        while True:
            i += 1
            try:
                start_date_stock = filtered_stocks[i]
                end_date_stock = filtered_stocks[i + 1]
            except IndexError:
                print 'finished list'
                break

            # print '%s/%s' % (i, len(filtered_stocks))
            if start_date_stock.company != end_date_stock.company:
                continue

            if start_date_stock.price == 0:
                continue

            increase_percentage = round(
                100 * (end_date_stock.price - start_date_stock.price) / start_date_stock.price, 2)

            if abs(increase_percentage) <= percentage:
                # print 'Price difference not big enough:', abs(increase_percentage), required_increase_percentage, abs(increase_percentage) < required_increase_percentage
                continue

            if not (
                        max_volume > start_date_stock.volume * start_date_stock.price > min_volume or max_volume > end_date_stock.volume * end_date_stock.price > min_volume):
                # print 'Turn over not big enough',
                continue

            results.append({
                'symbol': start_date_stock.company.symbol,
                'exchange': end_date_stock.company.exchange,
                'country': end_date_stock.company.country,
                'increase': increase_percentage,
                'start_price': start_date_stock.price,
                'end_price': end_date_stock.price,
                'volume': end_date_stock.volume * end_date_stock.price
            })

            i += 1 # plus 1 so it will jump the next record

        return results


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


