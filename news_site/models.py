# from django.db import models
from djongo import models
from decimal import Decimal


# Create your models here.

class Article(models.Model):
    """A news article."""

    _id = models.CharField("MongoDB ID", max_length=40, null=False, blank=False, primary_key=True)
    # scrape_id = models.CharField("Scrape ID",max_length=80, null=True, blank=True)
    headline = models.CharField("Headline", max_length=300, null=False, blank=False)
    date = models.DateField("Date", auto_now_add=True)
    source = models.CharField("Source", max_length=200, null=False, blank=False)
    url= models.URLField("URL", null=True) 
    # word_count = models.IntegerField("Word Count", null=True, blank=True)
    text = models.TextField("Text", blank=True)  
    subjectivity = models.DecimalField("Subjectivity", max_digits=25, decimal_places=25)
    polarity = models.DecimalField("Polarity", max_digits=25, decimal_places=25)
    disease = models.CharField("Disease", max_length=300, null=True, blank=True) 

    def __str__(self):
    
        """Returns string representation of the model."""
        return f"{self.source} | {self.disease} | {self.headline}"
