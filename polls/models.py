from django.db import models

# Class to determine the form of the entries in the database of
# recent rule violating drone users

class Person(models.Model):
    name = models.CharField('Name', primary_key = True, max_length=100)
    last_seen_date = models.DateTimeField('Last time seen')
    phone = models.CharField('Phone number', max_length=100)
    email = models.CharField('Email', max_length=100)
    closest_distance_in_meters = models.CharField('Closest distance', max_length=100)

