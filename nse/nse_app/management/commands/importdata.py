from argparse import ArgumentError
import logging

from django.db import models
import datetime
import csv
from django.core.management.base import BaseCommand
from nse_app.models import Index, IndexPrice

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import data from a CSV file'

    INDEX_NAME_CHOICES = ['NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY NEXT 50', 'NIFTY NEXT 50']

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)
        parser.add_argument('index_name', type=str, choices=self.INDEX_NAME_CHOICES)

    def handle(self, *args, **options):
        file_path = options['file_path']
        index_name = options['index_name']

        index, created = Index.objects.get_or_create(name=index_name)
        try:
            with open(file_path, 'r') as file_open:
                reader = csv.reader(file_open)
                next(reader)  
                for row in reader:
                    index_date = datetime.datetime.strptime(row[0], '%d-%b-%Y').strftime('%Y-%m-%d')
                    index_open, index_high, index_low, index_close, index_sharestraded, index_turnover = row[1:]
                    index_open, index_high, index_low, index_close = map(lambda x: round(float(x), 2), [index_open, index_high, index_low, index_close])
                    index_sharestraded = int(index_sharestraded) if index_sharestraded else 0
                    index_turnover = round(float(index_turnover), 2) if index_turnover else 0

                    daily_price, created = IndexPrice.objects.update_or_create(
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
                        self.stdout.write(self.style.WARNING(f'Data for {index_name} on {index_date} updated successfully'))

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        except ArgumentError as e:
            logger.error(f"Invalid argument: {str(e)}. Choose from: {', '.join(self.INDEX_NAME_CHOICES)}")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
