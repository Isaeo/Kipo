# load_data.py
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from search.models import Part
from django.contrib.postgres.search import SearchVector
from django.db.models import Value

class Command(BaseCommand):
    help = 'Load product data from CSV and corresponding datasheet .txt files'

    def load_datasheet_content(self, uid):
        """Loads the content of the corresponding datasheet based on UID."""
        datasheet_path = os.path.join(settings.BASE_DIR, 'data/datasheets_txt', f"{uid}.txt")
        try:
            with open(datasheet_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return ""  # Return an empty string if the file does not exist

    def handle(self, *args, **kwargs):
        csv_file_path = os.path.join(settings.BASE_DIR, 'data/product_data.csv')

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Insert the record without search_vector
                part, created = Part.objects.update_or_create(
                    mouser_part_number=row["Mouser Part Number"],
                    defaults={
                        "uid": int(row["UID"]),
                        "mfr_part_number": row["Mfr Part Number"],
                        "manufacturer": row["Mfr."],
                        "datasheet_url": row.get("Datasheet", ""),
                        "availability": row.get("Availability", ""),
                        "pricing": row.get("Pricing", ""),
                        "rohs": row.get("RoHS", ""),
                        "lifecycle": row.get("Lifecycle", ""),
                        "product_detail_url": row["Product Detail"],
                        "ip_rating": row.get("IP Rating", ""),
                        "product_category": row.get("Product", ""),
                        "contact_gender": row.get("Contact Gender", ""),
                        "termination_style": row.get("Termination Style", ""),
                    }
                )

                # Load the datasheet content
                datasheet_content = self.load_datasheet_content(row["UID"])

                # Define the search_vector with the specified structure
                search_vector = (
                    SearchVector('mfr_part_number', weight='A') +
                    SearchVector('manufacturer', weight='B') +
                    SearchVector('ip_rating', weight='C') +
                    SearchVector('termination_style', weight='C') +
                    SearchVector('product_category', weight='C') +
                    SearchVector(Value(datasheet_content), weight='B') +
                    SearchVector('contact_gender', weight='C')
                )

                # Update the search_vector in a separate query
                Part.objects.filter(mouser_part_number=part.mouser_part_number).update(
                    search_vector=search_vector
                )

        self.stdout.write(self.style.SUCCESS("Data loaded successfully"))
