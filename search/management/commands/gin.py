from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Add GIN index to search_vector field'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("CREATE INDEX product_search_vector_idx ON search_part USING GIN(search_vector);")
        self.stdout.write(self.style.SUCCESS("GIN index created successfully"))