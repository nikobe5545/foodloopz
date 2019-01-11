from enum import Enum

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db import models

from marketplace.validators import validate_organization_number


class TrackingModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Address(TrackingModel, models.Model):
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=12)
    city = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.address}\n{self.zip_code} {self.city}'


class OrganizationCertification(TrackingModel, models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class OrganizationCategory(TrackingModel, models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class Organization(TrackingModel, models.Model):
    organization_number = models.IntegerField(validators=[validate_organization_number])
    name = models.CharField(max_length=255)
    invoice_address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='invoice_address')
    visiting_address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='visiting_address',
                                            null=True, blank=True)
    number_of_employees = models.IntegerField(null=True)
    certifications = models.ManyToManyField(OrganizationCertification)
    has_alcohol_license = models.BooleanField(null=True)
    category = models.ForeignKey(OrganizationCategory, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.name} - {self.organization_number}'

    def get_serialization_dict(self):
        return {
            'id': self.id
        }


class Account(TrackingModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.email} of {self.organization}'

    def get_serialization_dict(self):
        return {
            'id': self.id,
            'organization': {
                'id': self.organization.id,

            },
            'dateJoined': self.user.date_joined,
            'email': self.user.email,
            'firstName': self.user.first_name,
            'lastName': self.user.last_name,
            'username': self.user.username
        }


class AdCategory(TrackingModel, models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class AdCertification(TrackingModel, models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class Measurement(Enum):
    KILOGRAM = 'Kg'
    LITER = 'Liter'


class Shipping(Enum):
    INCLUDED = 'Included'
    EXCLUDED = 'Excluded'
    BY_AGREEMENT = 'By agreement'


class Ad(TrackingModel, models.Model):
    product = models.CharField(max_length=255)
    text = models.TextField()
    category = models.ForeignKey(AdCategory, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    published_date = models.DateField(null=True, blank=True)
    unpublished_date = models.DateField(null=True, blank=True)
    price = models.FloatField(default=0)
    measurement = models.CharField(max_length=50, choices=[(entry.name, entry.value) for entry in Measurement])
    amount_per_unit = models.FloatField()
    quantity = models.IntegerField()
    total_weight = models.FloatField()
    shipping = models.CharField(max_length=50, choices=[(entry.name, entry.value) for entry in Shipping])
    certifications = models.ManyToManyField(AdCertification)
    image = CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return f'{self.product} published {self.published_date} by {self.account}'

    def get_serialization_dict(self):
        return {
            'id': self.id,
            'created': self.created.isoformat(),
            'updated': self.updated.isoformat(),
            'product': self.product,
            'text': self.text
        }


class Inquiry(TrackingModel, models.Model):
    product = models.CharField(max_length=255)
    text = models.TextField()
    image = CloudinaryField()
    price = models.FloatField(default=0)
    published_date = models.DateField(null=True)
    unpublished_date = models.DateField(null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product} published {self.published_date} by {self.account}'
