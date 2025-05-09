from django.shortcuts import redirect, render
from doctor.models import Appointment, Prescription_test, testOrder, Prescription
from hospital.models import Patient
from .models import Paymentpal
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import random
import string
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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


@csrf_exempt
@login_required(login_url="login")
def paypal_payment_request(request, pk, id):
    if request.user.is_patient:
        patient = Patient.objects.get(patient_id=pk)
        appointment = Appointment.objects.get(id=id)

        if appointment.payment_status == "confirmed":
            return redirect('patient-dashboard')
    else:
        return redirect('login')

    context = {
        "appointment": appointment,
        "patient": patient,
    }
    return render(request, 'payment.html', context)


@csrf_exempt
def payment_complete(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            patient_id = data.get('patient_id')
            appointment_id = data.get('appointment_id')
            
            patient = Patient.objects.get(patient_id=patient_id)
            appointment = Appointment.objects.get(id=appointment_id)
            
            appointment.payment_status = "confirmed"
            appointment.save()

            Paymentpal.objects.create(
                patient=patient,
                appointment=appointment,
                name=patient.username,
                email=patient.email,
                phone=patient.phone_number,
                address=patient.address,
                city="Qena",
                country="Egypt",
                transaction_id=data.get('paymentID'),
                consulation_fee=appointment.doctor.consultation_fee,
                currency_amount=appointment.doctor.consultation_fee,
                transaction_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                invoice_number=generate_random_invoice(),
                currency="USD",
                payment_type="appointment",
                status="confirmed",
            )

            return JsonResponse({'status': 'success', 'message': 'Payment saved successfully!'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        

@csrf_exempt
@login_required(login_url="login")
def paypal_payment_request_medicine(request, pk, id, pk2):
    if request.user.is_patient:
        patient = Patient.objects.get(patient_id=pk)
        test_order = testOrder.objects.get(id=id)
        prescription_test = Prescription_test.objects.get(test_id=pk2)

        if test_order.payment_status == "confirmed":
            return redirect('patient-dashboard')
    else:
        return redirect('login')

    context = {
        "test_order": test_order,
        "patient": patient,
        "prescription_test": prescription_test,
    }
    return render(request, 'payment_medicine.html', context)

@csrf_exempt
def medicine_payment_complete(request):
    data = json.loads(request.body)
    
    patient_id = data.get('patient_id')
    test_order_id = data.get('test_order_id')
    prescription_test_id = data.get('prescription_test_id')
    
    patient = Patient.objects.get(patient_id=patient_id)
    prescription_test = Prescription_test.objects.get(test_id=prescription_test_id)
    test_order = testOrder.objects.get(id=test_order_id)

    try:

        prescription_test.test_info_pay_status = "confirmed"
        prescription_test.save()

        test_order.payment_status = "confirmed"
        test_order.ordered = True
        test_order.trans_ID = data.get('paymentID')
        test_order.save()

        Paymentpal.objects.create(
            patient=patient,
            test_order=test_order,
            prescription=prescription_test.prescription,
            name=patient.username,
            email=patient.email,
            phone=patient.phone_number,
            address=patient.address,
            city="Qena",
            country="Egypt",
            transaction_id=data.get('paymentID'),
            report_fee=prescription_test.test_info_price,
            transaction_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            invoice_number=generate_random_invoice(),
            currency="USD",
            payment_type="Test order",
            status="confirmed",
        )

        return JsonResponse({'status': 'success', 'message': 'Payment saved successfully!'})

    except (Patient.DoesNotExist, Prescription_test.DoesNotExist, testOrder.DoesNotExist) as e:
        return JsonResponse({'status': 'error', 'message': f'Record not found: {str(e)}'}, status=400)
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': f'Invalid value: {str(ve)}'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)