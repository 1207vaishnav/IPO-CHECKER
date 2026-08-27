from django.db import models


class PAN(models.Model):
    pan_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name or self.pan_number


class IPO(models.Model):

    name = models.CharField(
        max_length=200
    )

    registrar = models.CharField(
        max_length=100
    )

    client_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

class Allotment(models.Model):
    pan = models.ForeignKey(PAN, on_delete=models.CASCADE)
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    shares = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.pan.pan_number} - {self.ipo.name}"