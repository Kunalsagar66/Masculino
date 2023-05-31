from email.policy import default
from ftplib import MAXLINE
from itertools import product
from random import choices
from django.db import models
from django.urls import reverse
# Create your models here.
from home.models import *
class Product(models.Model):
    product_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50,unique=True)
    description = models.CharField(max_length=200, blank=True)
    brand = models.CharField(max_length=50, blank=True)
    price = models.CharField(max_length=20)
    main_image = models.ImageField(default=None)
    side_image = models.ImageField(default=None)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

variation_category_choice=(
    ('size','size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    variation_category = models.CharField(max_length = 100, choices = variation_category_choice)
    variation_value = models.CharField(max_length = 100)
    is_active = models.BooleanField(default = True)
    created_date = models.DateTimeField(auto_now  = True)

    def __str__(self):
        return self.variation_value