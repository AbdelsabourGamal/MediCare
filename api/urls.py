from django.urls import path
from . import views

from rest_framework_simplejwt.views import ( # type: ignore
    TokenObtainPairView,
    TokenRefreshView,
)
app_name = 'api'
urlpatterns = [
    path('users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', views.getRoutes),
    path('patient_register/', views.PatientRegister.as_view()),
    path('doctor_register/', views.DoctorRegister.as_view()),
    path('admin_register/', views.AdminRegister.as_view()),

    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('password_reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('reset_password_confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),

    path('hospital/', views.getHospitals.as_view()),
    path('hospital/<int:pk>/', views.GetOneHospital.as_view()),

    path('doctor/', views.GetDoctors.as_view()),
    path('doctor/<int:pk>/', views.GetOneDoctor.as_view()),

    # path('patient_profile/', views.PatientProfiles.as_view()),
    path('patient_profile/<int:pk>/', views.PatientProfile.as_view()),

    path('appointment/', views.PatientAppointment.as_view()),

    path('prescription/', views.PatientPrescription.as_view()),
    path('prescription_medicine/', views.PatientPrescriptionMedicine.as_view()),
    path('prescription_test/', views.PatientPrescriptionTest.as_view()),

    path('all_prescription_data/', views.CombinedDataView.as_view()),


]

