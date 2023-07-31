from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Status(models.Model):
    GROUP_CHOICES = [
        ('New', 'Новый'),
        ('In progress', 'В работе'),
        ('Paid', 'Оплачен'),
        ('Done', 'Выполнен'),
        ('Rejected', 'Отказ'),
    ]

    name = models.CharField(max_length=100)
    group = models.CharField(max_length=25, choices=GROUP_CHOICES, default=GROUP_CHOICES[0][1])

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the Status Model object.

        Returns:
            str: Containing name.
        """
        return f'{self.name}'


class Lead(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    order = models.CharField(max_length=200)
    price = models.IntegerField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, default='+7(900)123-45-67')
    comment = models.TextField(blank=True, default=None)
    manager = models.ForeignKey(User, blank=True, null=True,
                                on_delete=models.SET_NULL, default=None)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=False, null=False, default='NoneOrg')
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the Status Model object.

        Returns:
            str: Containing the order, first name and last name.
        """
        return f'{self.order} - {self.first_name} {self.last_name}'
