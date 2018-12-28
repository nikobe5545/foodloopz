from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db import models

from marketplace.validators import validate_organization_number


class TrackingModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(TrackingModel, models.Model):
    organization_number = models.IntegerField(validators=[validate_organization_number])
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=12)
    city = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name} - {self.organization_number}'


class Account(TrackingModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.email} of {self.organization}'


class Category(TrackingModel, models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Ad(TrackingModel, models.Model):
    heading = models.CharField(max_length=255)
    text = models.TextField
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.heading} || {self.organization}'


class AdImage(TrackingModel, models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    image = CloudinaryField('image')
