from django.db import models
from django.contrib.auth import get_user_model

import uuid


User = get_user_model()


class Organization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, default='manager')


class MembershipInvitation(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False)
