from django.db import models

class Index(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class IndexPrice(models.Model):
    index = models.ForeignKey(Index, on_delete=models.CASCADE)
    date = models.CharField()  
    open = models.DecimalField(max_digits=10, decimal_places=2)  
    high = models.DecimalField(max_digits=10, decimal_places=2)  
    low = models.DecimalField(max_digits=10, decimal_places=2)  
    close = models.DecimalField(max_digits=10, decimal_places=2)  
    sharestraded = models.BigIntegerField()  
    turnover = models.DecimalField(max_digits=10    , decimal_places=2)  

    def __str__(self):
        return f"{self.index.name} - {self.date}"
