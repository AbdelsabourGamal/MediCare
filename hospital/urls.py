from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.hospital_home, name='hospital_home'),
    path('search/', views.search, name='search'),
    path('change-password/<int:pk>', views.change_password, name='change-password'),
    path('patient-dashboard/',views.patient_dashboard, name='patient-dashboard'),
    path('profile-settings/',views.profile_settings, name='profile-settings'),
    path('about-us/', views.about_us, name='about-us'),
    path('patient-register/', views.patient_register, name='patient-register'),
    path('logout/', views.logoutUser, name='logout'),
    path('multiple-hospital/', views.multiple_hospital, name='multiple-hospital'),
    path('hospital-profile/<int:pk>/', views.hospital_profile, name='hospital-profile'),
    path('data-table/', views.data_table, name='data-table'),
    path('hospital-department-list/<int:pk>/', views.hospital_department_list, name='hospital-department-list'),
    path('hospital-doctor-list/<int:pk>/', views.hospital_doctor_list, name='hospital-doctor-list'),
    path('hospital-doctor-register/<int:pk>/', views.hospital_doctor_register, name='hospital-doctor-register'),
    path('view-report/<int:pk>', views.view_report, name='view-report'),
    path('test-cart/<int:pk>/', views.test_cart, name='test-cart'),
    path('prescription-view/<int:pk>', views.prescription_view, name='prescription-view'),
    path('pres_pdf/<int:pk>/',views.prescription_pdf, name='pres_pdf'),
    path('report_pdf/<int:pk>/',views.report_pdf, name='report_pdf'),
    path('test-single/<int:pk>/', views.test_single, name='test-single'),
    path('test-remove-cart/<int:pk>/', views.test_remove_cart, name='test-remove-cart'),
    path('test-add-to-cart/<int:pk>/<int:pk2>/', views.test_add_to_cart, name='test-add-to-cart'),
    path('delete-prescription/<int:pk>/', views.delete_prescription, name='delete-prescription'),
    path('delete-report/<int:pk>/', views.delete_report, name='delete-report'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
