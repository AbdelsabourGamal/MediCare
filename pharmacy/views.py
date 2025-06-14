import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from hospital.models import Patient
from pharmacy.models import Medicine, Cart, Order
from .utils import searchMedicines
from django.views.decorators.csrf import csrf_exempt
from paypal.models import Payment


@csrf_exempt
@login_required(login_url="login")
def pharmacy_single_product(request,pk):
     if request.user.is_authenticated and request.user.is_patient:

        patient = Patient.objects.get(user=request.user)
        medicines = Medicine.objects.get(serial_number=pk)
        orders = Order.objects.filter(user=request.user, ordered=False)
        carts = Cart.objects.filter(user=request.user, purchased=False)
        if carts.exists() and orders.exists():
            order = orders[0]
            context = {'patient': patient, 'medicines': medicines,'carts': carts,'order': order, 'orders': orders}
            return render(request, 'Pharmacy/product-single.html',context)
        else:
            context = {'patient': patient, 'medicines': medicines,'carts': carts,'orders': orders}
            return render(request, 'Pharmacy/product-single.html',context)
     else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def pharmacy_shop(request):
    if request.user.is_authenticated and request.user.is_patient:

        patient = Patient.objects.get(user=request.user)
        medicines = Medicine.objects.all()
        orders = Order.objects.filter(user=request.user, ordered=False)
        carts = Cart.objects.filter(user=request.user, purchased=False)

        medicines, search_query = searchMedicines(request)

        if carts.exists() and orders.exists():
            order = orders[0]
            context = {'patient': patient, 'medicines': medicines,'carts': carts,'order': order, 'orders': orders, 'search_query': search_query}
            return render(request, 'Pharmacy/shop.html', context)
        else:
            context = {'patient': patient, 'medicines': medicines,'carts': carts,'orders': orders, 'search_query': search_query}
            return render(request, 'Pharmacy/shop.html', context)

    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def add_to_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:

        item = get_object_or_404(Medicine, pk=pk)
        order_item = Cart.objects.get_or_create(item=item, user=request.user, purchased=False)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item[0].quantity += 1
                order_item[0].save()
                return redirect('pharmacy_shop')
            else:
                order.orderitems.add(order_item[0])
                return redirect('pharmacy_shop')
        else:
            order = Order(user=request.user)
            order.save()
            order.orderitems.add(order_item[0])
            return redirect('pharmacy_shop')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def cart_view(request):
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        carts = Cart.objects.filter(user=request.user, purchased=False)
        orders = Order.objects.filter(user=request.user, ordered=False)
        if carts.exists() and orders.exists():
            order = orders[0]
            context = {'carts': carts,'order': order,'patient':patient}
            return render(request, 'Pharmacy/cart.html', context)
        else:
            messages.warning(request, "You don't have any item in your cart!")
            return redirect('pharmacy_shop')
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')

@csrf_exempt
@login_required(login_url="login")
def remove_from_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:

        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                order.orderitems.remove(order_item)
                order_item.delete()
                messages.warning(request, "This item was remove from your cart!")
                return redirect('cart')
            else:
                messages.info(request, "This item was not in your cart")
                return redirect('pharmacy_shop')
        else:
            messages.info(request, "You don't have an active order")
            return redirect('pharmacy_shop')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return redirect('login')


@csrf_exempt
@login_required(login_url="login")
def increase_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:

        patient = Patient.objects.get(user=request.user)
        medicines = Medicine.objects.all()
        carts = Cart.objects.filter(user=request.user, purchased=False)
        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                if order_item.quantity >= 1:
                    order_item.quantity += 1
                    order_item.save()
                    messages.warning(request, f"{item.name} quantity has been updated")
                    context = {'carts': carts,'order': order}
                    return redirect('cart')
            else:
                messages.warning(request, f"{item.name} is not in your cart")
                context = {'patient': patient,'medicines': medicines}
                return render(request, 'Pharmacy/shop.html', context)
        else:
            messages.warning(request, "You don't have an active order")
            context = {'patient': patient,'medicines': medicines}
            return render(request, 'Pharmacy/shop.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def decrease_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:

        patient = Patient.objects.get(user=request.user)
        medicines = Medicine.objects.all()
        carts = Cart.objects.filter(user=request.user, purchased=False)
        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.warning(request, f"{item.name} quantity has been updated")
                    context = {'carts': carts,'order': order}
                    return redirect('cart')
                else:
                    order.orderitems.remove(order_item)
                    order_item.delete()
                    messages.warning(request, f"{item.name} item has been removed from your cart")
                    context = {'carts': carts,'order': order}
                    return redirect('cart')
            else:
                messages.info(request, f"{item.name} is not in your cart")
                context = {'patient': patient,'medicines': medicines}
                return render(request, 'Pharmacy/shop.html', context)
        else:
            messages.info(request, "You don't have an active order")
            context = {'patient': patient,'medicines': medicines}
            return render(request, 'Pharmacy/shop.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def checkout(request, pk, id):
    if request.user.is_patient:
        patient = Patient.objects.get(patient_id=pk)
        order = Order.objects.get(id=id)
        print(order.final_bill )
        if order.payment_status == "confirmed":
            return redirect('patient-dashboard')
    else:
        return redirect('login')

    context = {
        "order": order,
        "patient": patient,
    }
    return render(request, 'Pharmacy/checkout.html', context)


@csrf_exempt
def checkout_complete(request):
    data = json.loads(request.body)

    patient_id = data.get('patient_id')
    order_id = data.get('order_id')

    patient = Patient.objects.get(patient_id=patient_id)
    order = Order.objects.get(id=order_id)

    cart = order.orderitems.all()
    print(order)
    try:


        order.ordered = True
        order.payment_status = "confirmed"
        order.trans_ID = data.get('paymentID')
        order.save()

        for cart_item in cart:
            cart_item.purchased = True
            cart_item.save()

        Payment.objects.create(
            patient=patient,
            pharmacy_order=order,
            name=patient.username,
            email=patient.email,
            phone=patient.phone_number,
            address=patient.address,
            city="Qena",
            country="Egypt",
            transaction_id=data.get('paymentID'),
            currency_amount=order.final_bill,
            transaction_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            currency="USD",
            payment_type="Pharmacy order",
            status="confirmed",
        )

        return JsonResponse({'status': 'success', 'message': 'Payment saved successfully!'})

    except (Patient.DoesNotExist, patient_id.DoesNotExist, order.DoesNotExist) as e:
        return JsonResponse({'status': 'error', 'message': f'Record not found: {str(e)}'}, status=400)
    except ValueError as ve:
        return JsonResponse({'status': 'error', 'message': f'Invalid value: {str(ve)}'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
