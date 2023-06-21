from django.db import models
import uuid
from django.contrib.auth import get_user_model


User = get_user_model()


class Organization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class MembershipInvitation(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    