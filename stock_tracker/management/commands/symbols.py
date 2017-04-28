from django.core.management.base import BaseCommand

from stock_tracker.utils import SymbolsJson


class Command(BaseCommand):
    help = 'Fills database with company data in Symbols file'

    def handle(self, *args, **options):
        SymbolsJson.create()