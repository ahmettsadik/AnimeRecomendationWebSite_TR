import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from searchanime.models import Anime

class Command(BaseCommand):
    help = 'Load anime data from CSV file'

    def handle(self, *args, **kwargs):
        path = 'sondatabase.csv'
        
        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                with transaction.atomic():
                    for row in reader:
                        try:
                            Anime.objects.create(
                                mal_id=int(row['mal_id']),
                                english_name=row['english_name'],
                                score=float(row['score']),
                                genres=row['genres'],
                                popularity=int(row['popularity'])
                            )
                        except ValueError as e:
                            self.stdout.write(self.style.ERROR(f"Error processing row {row}: {e}"))
            
            self.stdout.write(self.style.SUCCESS('Successfully loaded anime data'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"The file {path} does not exist."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))