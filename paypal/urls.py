from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('payment_request/<int:pk>/<int:id>/', views.paypal_payment_request, name='payment_request'),
    path('payment_complete/', views.payment_complete, name='payment_complete'), # type: ignore
    path('payment_request_test/<int:pk>/<int:id>/', views.paypal_payment_request_test, name='payment_request_test'),
    path('test_payment_complete/', views.test_payment_complete, name='test_payment_complete'),



]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)