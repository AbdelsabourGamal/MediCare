from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('pay/<int:id>/', views.paypal_payment, name='paypal_payment'),
    path('paypal_payment_request/<int:pk>/<int:id>/', views.paypal_payment_request, name='paypal_payment_request'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)