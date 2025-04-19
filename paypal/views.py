from django.shortcuts import redirect, render
from doctor.models import Appointment
from hospital.models import Patient
from .models import Paymentpal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import random
import string
from datetime import datetime

# Create your views here.
def paypal_payment(request,id):
    appointment = Appointment.objects.get(id=id)


    context = {
        "appointment":appointment,
    }
    return render(request, "payment.html", context)

def generate_random_invoice():
    N = 4
    string_var = ""
    string_var = ''.join(random.choices(string.digits, k=N))
    string_var = "#INV-" + string_var
    return string_var

def generate_random_string():
    N = 8
    string_var = ""
    string_var = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=N))
    string_var = "PAYPAL_TEST_" + string_var
    return string_var

@csrf_exempt
@login_required(login_url="login")
def paypal_payment_request(request, pk, id):
    if request.user.is_patient :
        patient = Patient.objects.get(patient_id=pk)
        appointment = Appointment.objects.get(id=id)

        if appointment.payment_status == "pending":
            invoice_number = generate_random_invoice()

            appointment.payment_status = "confirmed"
            appointment.save()

            payment = Paymentpal()

            payment.patient = patient
            payment.appointment = appointment
            payment.name = patient.username
            payment.email = patient.email
            payment.phone = patient.phone_number
            payment.address = patient.address
            payment.city = "Qena"
            payment.country = "Egypt"
            payment.transaction_id = generate_random_string()

            payment.consulation_fee = appointment.doctor.consultation_fee
            payment.currency_amount = appointment.doctor.consultation_fee

            payment.transaction_date = datetime.now()
            payment.invoice_number = invoice_number

            payment.urrency = "USD"
            
            payment.payment_type = "appointment"
            payment.status = "confirmed"
            payment.save()

        else:
            return redirect('patient-dashboard')
    else:
        return redirect('login')

    context = {
        "appointment":appointment,
        "patient": patient,
    }
    return render(request, 'payment.html', context)