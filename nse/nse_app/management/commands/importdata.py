import os
import csv
import logging
from django.core.management.base import BaseCommand
from nse_app.models import Index, IndexPrice

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        file_path = options['file_path']
        index_name = os.path.basename(file_path).split('-')[0]  

        index, created = Index.objects.get_or_create(name=index_name)
        
        # try:
        with open(file_path, 'r') as file_open:
                reader = csv.reader(file_open)
                next(reader)  # Skip the header row
                for row in reader:
                    index_date, index_open, index_high, index_low, index_close, index_sharestraded, index_turnover = row
                    index_open, index_high, index_low, index_close = map(lambda x: round(float(x), 2), [index_open, index_high, index_low, index_close])
                    index_sharestraded = int(index_sharestraded) if row[5] else 0
                    index_turnover = round(float(index_turnover), 2)if row[6] else 0

                    daily_price, created = IndexPrice.objects.get_or_create(
                        index=index,
                        date=index_date,
                        defaults={'open': index_open,
                                  'high': index_high, 
                                  'low': index_low, 
                                  'close': index_close, 
                                  'sharestraded': index_sharestraded, 
                                  'turnover': index_turnover},
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Successfully imported data for {index_name} on {index_date}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Data for {index_name} on {index_date} already exists'))
        # except FileNotFoundError:
        #     logger.error(f"File not found: {file_path}")
        # except Exception as e:
        #     logger.error(f"An error occurred: {str(e)}")
