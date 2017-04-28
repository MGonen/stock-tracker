from django.core.management.base import BaseCommand

from stock_tracker.utils import GetHistoricStockInfo


class Command(BaseCommand):
    help = 'Updates the permissions to correspond with the HostPrimaries'


    def handle(self, *args, **options):
        GetHistoricStockInfo.main()