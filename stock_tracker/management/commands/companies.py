from django.core.management.base import BaseCommand

from stock_tracker.utils import FillCompanyDB


class Command(BaseCommand):
    help = 'Fills database with company data in Symbols file'

    def handle(self, *args, **options):
        FillCompanyDB.main()