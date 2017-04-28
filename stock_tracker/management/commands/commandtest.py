from django.core.management.base import BaseCommand

from stock_tracker.models import Stock, Company


class Command(BaseCommand):
    help = 'Fills database with company data in Symbols file'

    def handle(self, *args, **options):
        company = Company.objects.all()[0]
        s = Stock(company=company, price=1, volume=1)
        s.save()
