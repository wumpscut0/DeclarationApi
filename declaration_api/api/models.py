from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=40, unique=True, editable=False)
    requests_count = models.IntegerField(default=0)


class Declaration(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    author = models.ForeignKey("Author", on_delete=models.PROTECT, related_name="declarations")
    header = models.CharField(max_length=1000, null=True)
    views = models.IntegerField(null=True)
    position = models.IntegerField(null=True)

    def as_dict(self):
        return {
            "id": self.id,
            "header": self.header,
            "author": self.author.as_dict(),
            "views": self.views,
            "position": self.position,
        }


class Author(models.Model):
    name = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=40, null=True)
    address = models.CharField(max_length=50, null=True)

    def as_dict(self):
        return {
            "name": self.name,
            "phone": self.phone,
            "address": self.address
        }
