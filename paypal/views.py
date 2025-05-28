from django.shortcuts import redirect, render
from doctor.models import Appointment, Prescription_test, testOrder, testCart
from hospital.models import Patient
from hospital.views import test_cart
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import random
import string
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
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

            Payment.objects.create(
                patient=patient,
                appointment=appointment,
                name=patient.username,
                email=patient.email,
                phone=patient.phone_number,
                address=patient.address,
                city="Qena",
                country="Egypt",
                transaction_id=data.get('paymentID'),
                currency_amount=appointment.doctor.consultation_fee,
                transaction_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                currency="USD",
                payment_type="appointment",
                status="confirmed",
            )

            return JsonResponse({'status': 'success', 'message': 'Payment saved successfully!'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        

@csrf_exempt
@login_required(login_url="login")
def paypal_payment_request_test(request, pk, id):
    if request.user.is_patient:
        patient = Patient.objects.get(patient_id=pk)
        test_order = testOrder.objects.get(id=id)

        if test_order.payment_status == "confirmed":
            return redirect('patient-dashboard')
    else:
        return redirect('login')

    context = {
        "test_order": test_order,
        "patient": patient,
    }
    return render(request, 'payment_test.html', context)

@csrf_exempt
def test_payment_complete(request):
    data = json.loads(request.body)

    patient_id = data.get('patient_id')
    test_order_id = data.get('test_order_id')
    
    patient = Patient.objects.get(patient_id=patient_id)
    test_order = testOrder.objects.get(id=test_order_id)
    prescription_test = test_order.prescription_test
    test_cart = test_order.orderitems.all()
    print(test_cart)
    try:

        prescription_test.test_info_pay_status = "confirmed"
        prescription_test.save()
        
        for cart_item in test_cart:
            cart_item.purchased = True
            cart_item.save()

        test_order.prescription_test=prescription_test
        test_order.payment_status = "confirmed"
        test_order.ordered = True
        test_order.trans_ID = data.get('paymentID')
        test_order.save()

        Payment.objects.create(
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
            currency_amount=prescription_test.test_info_price,
            transaction_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
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
