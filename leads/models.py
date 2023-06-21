from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f'{self.name}'


class Lead(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    order = models.CharField(max_length=200)
    price = models.IntegerField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=False, default='+7(900)123-45-67')
    comment = models.TextField(blank=True, default=None)
    # organization = models.ForeignKey(Organisation, blank=False, on_delete=models.CASCADE)
    # manager = models.ForeignKey(Manager, blank=True, null=True, 
    #                            on_delete=models.SET_NULL, default=None)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name} - {self.order}'

