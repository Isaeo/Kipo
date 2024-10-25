import os
from django.conf import settings
from django.db import models
from django.contrib.postgres.search import SearchVectorField

class Part(models.Model):
    mouser_part_number = models.CharField(max_length=100, primary_key=True)  # Primary Key
    uid = models.IntegerField()
    mfr_part_number = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    datasheet_url = models.URLField(max_length=300, blank=True, null=True)
    availability = models.CharField(max_length=50, blank=True, null=True)
    pricing = models.CharField(max_length=50, blank=True, null=True)
    rohs = models.CharField(max_length=100, blank=True, null=True)
    lifecycle = models.CharField(max_length=100, blank=True, null=True)
    product_detail_url = models.URLField(max_length=500)
    ip_rating = models.CharField(max_length=20, blank=True, null=True)
    product_category = models.CharField(max_length=100, blank=True, null=True)
    contact_gender = models.CharField(max_length=100, blank=True, null=True)
    termination_style = models.CharField(max_length=100, blank=True, null=True)

    # Full-text search vector field for PostgreSQL
    search_vector = SearchVectorField(null=True, editable=False)

    def load_datasheet_content(self):
        """Dynamically loads the content of the corresponding datasheet based on UID."""
        datasheet_path = os.path.join(settings.BASE_DIR, 'data/datasheets_txt', f"{self.uid}.txt")
        try:
            with open(datasheet_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "Datasheet content not available."

    def __str__(self):
        return f"{self.manufacturer} - {self.mfr_part_number}"
