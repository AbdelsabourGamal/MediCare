from django.db import models
from doctor.models import Appointment, testOrder, Prescription
from hospital.models import Patient
from pharmacy.models import Order

# Create your models here.


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    test_order = models.ForeignKey(testOrder, on_delete=models.SET_NULL, null=True, blank=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    pharmacy_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    payment_type = models.CharField(max_length=200, null=True, blank=True)
    
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    currency_amount = models.CharField(max_length=255, null=True, blank=True)
    
    status = models.CharField(max_length=255, null=True, blank=True)
    transaction_date = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.patient} {self.payment_type}'
