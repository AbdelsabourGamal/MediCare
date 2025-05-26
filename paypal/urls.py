from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('payment_request/<int:pk>/<int:id>/', views.paypal_payment_request, name='payment_request'),
    path('payment_complete/', views.payment_complete, name='payment_complete'), # type: ignore
    path('payment_request_medicine/<int:pk>/<int:id>/<int:pk2>/', views.paypal_payment_request_medicine, name='payment_request_medicine'),
    path('medicine_payment_complete/', views.medicine_payment_complete, name='medicine_payment_complete'),


    # path('payment_request_pharmacy/<int:pk>/<int:id>/<int:pk2>/', views.paypal_payment_request_pharmacy, name='payment_request_pharmacy'),
    # path('pharmacy_payment_complete/', views.pharmacy_payment_complete, name='pharmacy_payment_complete'),



]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)