from django.utils import timezone

import requests
import scriptine
import pprint
import csv
import xlrd
import json
import time

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
            cls.fill_symbol_db()

        else:
            print 'Symbol DB already filled'

    @classmethod
    def fill_symbol_db(cls):
        symbols_dicts = cls.get_symbol_dicts()

        print '\nCompany info will now be saved into DB'
        for number, symbol_dict in enumerate(symbols_dicts):
            if number % 100 == 0:
                print 'Now processing: %s/%s' % (number, len(symbols_dicts))
            c = Company(symbol=symbol_dict['symbol'], name=symbol_dict['name'], exchange=symbol_dict['exchange'], country=symbol_dict['country'])
            c.save()

        print 'All data has been saved to the DB\n'

    @classmethod
    def get_symbol_dicts(cls):
        path = scriptine.path(__file__).parent.parent.joinpath('symbols')
        with open(str(path), str('r')) as f:
            content = f.read()

        return json.loads(content)


class GetDailyStockInfo():

    @classmethod
    def main(cls):
        print '\n Stock Info will now be fetched and saved'

        companies = list(Company.objects.all())
        chunks = [companies[x:x + 1000] for x in xrange(0, len(companies), 1000)]

        prev_len = len(Stock.objects.all())
        for number, chunk in enumerate(chunks):
            print 'Proccessing chunk number: %s/%s' % (number + 1, len(chunks))
            url = cls._create_url(chunk)

            print '- request to be sent'
            data = cls._request_csv_data(url)
            print '- response received'

            cls._save_csv_data(data)
            print '- data saved'

            print '- Number of new entries:', len(Stock.objects.all()) - prev_len
            prev_len = len(Stock.objects.all())

            time.sleep(3)

        print 'All available stock data has been saved\n'

    @classmethod
    def _get_stock_symbols(cls, exchange):
        return Company.objects.filter(exchange=exchange)

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
    def _request_csv_data(cls, url):
        with requests.Session() as s:
            download = s.get(url)

            decoded_content = download.content.decode('utf-8')

            data = csv.reader(decoded_content.splitlines(), delimiter=str(u','))
            return list(data)

    @classmethod
    def _save_csv_data(cls, data):
        for item in data:
            try:
                price = float(item[1])
                volume = int(item[2])
                date = timezone.now().date() - timezone.timedelta(days=1)
            except IndexError as e:
                print 'Index Error:', e
                print data
                continue
            except ValueError:
                continue

            company = Company.objects.get(symbol=item[0])

            if Stock.objects.filter(company=company, date=date):
                print 'already exists:', Stock.objects.filter(company=company, date=date)
                continue

            s = Stock(company=company, price=price, volume=volume, date=date)
            s.save()


class GetHistoricStockInfo():
    @classmethod
    def main(cls):
        print '\n Historic Stock Info will now be fetched and saved'
        cls.get_data_all_stocks()
        print 'All available stock data has been saved\n'
        return

    @classmethod
    def get_data_all_stocks(cls):
        companies = list(Company.objects.filter(historic_collected=False))
        all_companies_length = len(Company.objects.all())
        prev_len = len(Stock.objects.all())
        for number, company in enumerate(companies):
            print 'Proccessing company: %s -  %s/%s' % (company.symbol, all_companies_length-len(companies)+number+1, all_companies_length)

            try:
                cls.remove_stock_data(company)
                cls.get_stock_data(company)
                company.historic_collected = True
                company.save()

                print '- Number of new entries:', len(Stock.objects.all()) - prev_len
                prev_len = len(Stock.objects.all())
                time.sleep(3)

            except UnicodeEncodeError:
                print "\n\n\nUnicode Encoding error caught!\n\n\n"
                continue

    @classmethod
    def remove_stock_data(cls, company):
        filtered_stocks = Stock.objects.filter(company=company)
        print 'before deletion:',len(filtered_stocks)
        Stock.objects.filter(company=company).delete()
        print 'after deletion:', len(Stock.objects.filter(company=company))

    @classmethod
    def get_stock_data(cls, company):
        url = cls._create_url(company)

        print '- request to be sent'
        data = cls._request_csv_data(url)
        print '- response received'

        cls._save_csv_data(data, company.symbol)
        print '- data saved'


    @classmethod
    def _get_stock_symbols(cls, exchange):
        return Company.objects.filter(exchange=exchange)

    @classmethod
    def _create_url(cls, company):
        stock_symbol = company.symbol
        print 'Stock symbol:', stock_symbol
        url = "http://ichart.finance.yahoo.com/table.csv?s=%s&g= spa2" % (stock_symbol)
        return url

    @classmethod
    def _request_csv_data(cls, url):
        with requests.Session() as s:
            download = s.get(url)

            decoded_content = download.content.decode('utf-8')

            data = csv.reader(decoded_content.splitlines(), delimiter=str(u','))
            return list(data)


    @classmethod
    def _save_csv_data(cls, data, symbol):
        for item in data:
            try:
                price = float(item[4])
                volume = int(item[5])
                date = item[0]
            except IndexError as e:
                print 'Index Error:', e
                print data
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


            s = Stock(company=company, price=price, volume=volume, date=date)
            s.save()


