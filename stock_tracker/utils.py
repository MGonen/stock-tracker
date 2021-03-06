from django.utils import timezone
import datetime

import requests
import scriptine
import pprint
import csv
import xlrd
import json
import time
from django.db.models import Q

from stock_tracker.models import Company, Stock

# http://usfundamentals.com
# token = 'PFUfNoPutTzEl1AEDeI_Yw'



class SymbolsJson():

    @classmethod
    def create(cls):
        path = scriptine.path(r'/home/michael/Documents/Asaf Stocks/Yahoo Symbols.xlsx')
        symbols = cls.get_symbols(path)
        cls.write_symbols(symbols)
        print 'finished'


    @classmethod
    def get_symbols(cls, path):
        symbol_list = []

        book = xlrd.open_workbook(path)
        stocks_sheet = book.sheet_by_index(0)

        for row in range(4, stocks_sheet.nrows):
            symbol = stocks_sheet.cell(row, 0).value
            name = stocks_sheet.cell(row, 1).value
            exchange = stocks_sheet.cell(row, 2).value
            country = stocks_sheet.cell(row, 3).value

            symbol_list.append({'symbol': symbol, 'name': name, 'exchange': exchange, 'country': country})

        return symbol_list

    @classmethod
    def write_symbols(cls, symbols):
        symbols_json = json.dumps(symbols)
        path = scriptine.path(__file__).parent.parent.joinpath('symbols')
        with open(path, 'w') as f:
            f.write(symbols_json)


class FillCompanyDB():
    @classmethod
    def main(cls):
        if not Company.objects.all():
            records = cls.create_records()
            cls.save_records(records)
            print 'All data has been saved to the DB\n'

        else:
            print 'Symbol DB already filled'

    @classmethod
    def create_records(cls):
        companies = []
        symbols_dicts = cls.get_symbol_dicts()

        print '\nCompany info will now be saved into DB'
        for number, symbol_dict in enumerate(symbols_dicts):
            companies.append(Company(symbol=symbol_dict['symbol'], name=symbol_dict['name'], exchange=symbol_dict['exchange'], country=symbol_dict['country']))
        return companies

    @classmethod
    def save_records(cls, records):
        chunks = [records[x:x + 500] for x in xrange(0, len(records), 500)]
        for number, chunk in enumerate(chunks):
            print 'Now Saving: %s/%s' % (number, len(chunks))
            Company.objects.bulk_create(chunk)

    @classmethod
    def get_symbol_dicts(cls):
        path = scriptine.path(__file__).parent.parent.joinpath('symbols')
        with open(str(path), str('r')) as f:
            content = f.read()

        return json.loads(content)


class GetStockInfo():
    @classmethod
    def main(cls):
        print '\n Stock Info will now be fetched and saved'
        records = list(cls._get_data())
        records = [item for sublist in records for item in sublist]
        cls._save_records(records)
        print 'All available stock data has been saved\n'

    @classmethod
    def _get_data(cls):
        # Will be overwritten
        return

    @classmethod
    def _get_stock_symbols(cls, exchange):
        return Company.objects.filter(exchange=exchange)

    @classmethod
    def _request_csv_data(cls, url):
        with requests.Session() as s:
            download = s.get(url)

            decoded_content = download.content.decode('utf-8')

            data = csv.reader(decoded_content.splitlines(), delimiter=str(u','))
            return list(data)

    @classmethod
    def _save_records(cls, records):
        if not records:
            print '-NO RECORDS SAVED'
            return

        chunks = [records[x:x + 500] for x in xrange(0, len(records), 500)]
        for number, chunk in enumerate(chunks):
            Stock.objects.bulk_create(chunk)


class GetDailyStockInfo(GetStockInfo):
    @classmethod
    def _get_data(cls):
        companies = list(Company.objects.all())
        chunks = [companies[x:x + 1000] for x in xrange(0, len(companies), 1000)]

        for number, chunk in enumerate(chunks):
            print 'Proccessing chunk number: %s/%s' % (number + 1, len(chunks))
            yield cls.process_chunk(chunk)
            time.sleep(1)

    @classmethod
    def process_chunk(cls, chunk):
        url = cls._create_url(chunk)
        data = cls._request_csv_data(url)
        records = cls._create_records(data)
        return records

    @classmethod
    def _create_url(cls, stocks):
        companies_string = ''
        stock_symbols = map(lambda x:x.symbol, stocks)
        for symbol in stock_symbols:
            companies_string += symbol + '+'

        companies_string = companies_string[:-1]

        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=spa2' % (companies_string,)
        return url

    @classmethod
    def _create_records(cls, data):
        records = []
        for item in data:
            try:
                price = float(item[1])
                volume = int(item[2])
                date = timezone.now().date() - timezone.timedelta(days=1)
            except IndexError as e:
                continue
            except ValueError:
                continue

            company = Company.objects.get(symbol=item[0])

            if Stock.objects.filter(company=company, date=date):
                print 'already exists:', Stock.objects.filter(company=company, date=date)
                continue

            records.append(Stock(company=company, price=price, volume=volume, date=date))
        return records


class GetHistoricStockInfo(GetStockInfo):
    @classmethod
    def main(cls):
        for i in range(50):
            print '\n Historic Stock Chunk %s/50' % (i+1,)
            records = list(cls._get_data())
            records = [item for sublist in records for item in sublist]
            cls._save_records(records)
            print 'All available stock data has been saved\n'

    @classmethod
    def _get_data(cls):
        companies = list(Company.objects.filter(historic_collected=False))
        total_number = 100

        for number, company in enumerate(companies[:total_number]):
            print "Processing Company %i/%i" % (number, total_number)
            try:
                cls.remove_stock_data(company)
                records = cls.get_stock_data(company)
                if records:
                    yield records
                company.historic_collected = True
                company.save()

                time.sleep(1)

            except (UnicodeEncodeError, IndexError, ValueError):
                continue

    @classmethod
    def remove_stock_data(cls, company):
        Stock.objects.filter(company=company).delete()

    @classmethod
    def get_stock_data(cls, company):
        url = cls._create_url(company)
        data = cls._request_csv_data(url)
        return cls._create_records(data, company.symbol)


    @classmethod
    def _create_url(cls, company):
        stock_symbol = company.symbol
        url = "http://ichart.finance.yahoo.com/table.csv?s=%s&g= spa2" % (stock_symbol)
        return url

    @classmethod
    def _create_records(cls, data, symbol):
        records = []
        for item in data:
            try:
                price = float(item[4])
                volume = int(item[5])
                date = item[0]
            except IndexError as e:
                return
            except ValueError:
                continue

            company = Company.objects.get(symbol=symbol)

            if Stock.objects.filter(company=company, date=date):
                print 'already exists:', Stock.objects.filter(company=company, date=date)
                continue

            if date[:4] not in ['2017', '2016', '2015', '2014']:
                break

            if volume < 1000:
                continue

            records.append(Stock(company=company, price=price, volume=volume, date=date))
        return records


class GetResults():
    @classmethod
    def main(cls, min_percentage, max_percentage, min_volume, max_volume, start_date, end_date):
        min_percentage = float(min_percentage)
        max_percentage = float(max_percentage)
        min_volume = int(float(min_volume) * 1000000)
        max_volume = int(float(max_volume) * 1000000)

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

        start_date_stocks = cls.get_date_filtered_stocks(start_date)
        end_date_stocks = cls.get_date_filtered_stocks(end_date)
        date_filtered_stocks = (start_date_stocks | end_date_stocks).order_by('company', 'date')

        filtered_stocks = date_filtered_stocks.filter(company__country__in=whitelist_countries)
        part_of_pair = False

        for i in range(len(filtered_stocks) - 1):
            if filtered_stocks[i].company != filtered_stocks[i + 1].company:
                part_of_pair = False
                continue

            else:
                if part_of_pair == True:
                    print 'Already part of pair'
                start_date_stock = filtered_stocks[i]
                end_date_stock = filtered_stocks[i + 1]
                part_of_pair = True

            yield cls.check_stock_pair(start_date_stock, end_date_stock, min_percentage, max_percentage, min_volume, max_volume)

    @classmethod
    def get_date_filtered_stocks(cls, org_date):
        n = 0
        stocks = Stock.objects.filter(date=org_date)
        while n < 7:
            n += 1
            for i in [1, -1]:
                found_companies = map(lambda x: x[0], stocks.values_list('company'))
                date = cls.get_date(org_date, n, i)
                date_stocks = Stock.objects.filter(date=date)
                stocks = stocks | date_stocks.exclude(company__in=found_companies)
        return stocks

    @classmethod
    def get_date(cls, date, n, i):
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        date -= datetime.timedelta(days= n*i*1)
        return date.strftime('%Y-%m-%d')

    @classmethod
    def check_stock_pair(cls, start_date_stock, end_date_stock, min_percentage, max_percentage, min_volume, max_volume):
        if max_percentage < min_percentage:
            min_percentage, max_percentage = max_percentage, min_percentage # if the user accidentally makes a mistake in min and max, it is corrected here

        if max_volume < min_volume:
            min_volume, max_volume = max_volume, min_volume # if the user accidentally makes a mistake in min and max, it is corrected here

        if not start_date_stock or not end_date_stock:
            # print 'Missing one of the dates'
            return

        if start_date_stock.price == 0:
            increase_percentage = 0
        else:
            increase_percentage = round(100 * (end_date_stock.price - start_date_stock.price) / start_date_stock.price,
                                        2)

        if  increase_percentage < min_percentage  or increase_percentage > max_percentage:
            # print 'Price difference not big enough:', abs(increase_percentage), required_increase_percentage, abs(increase_percentage) < required_increase_percentage
            return

        if not (max_volume > start_date_stock.volume * start_date_stock.price > min_volume or max_volume > end_date_stock.volume * end_date_stock.price > min_volume):
            # print 'Turn over not big enough',
            return

        return [
            start_date_stock.company.name,
            start_date_stock.company.symbol,
            start_date_stock.company.exchange,
            start_date_stock.company.country,
            increase_percentage,
            start_date_stock.price,
            end_date_stock.price,
            end_date_stock.volume * end_date_stock.price,
            start_date_stock.date,
            end_date_stock.date
        ]


