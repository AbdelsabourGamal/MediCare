from ast import mod
from os import access
import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from doctor.views import patient_id
from hospital_admin.views import appointment_list
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from rest_framework.response import Response
from .serializers import DoctorSerializer, HospitalSerializer, PatientRegisterSerializer, DoctorRegisterSerializer, AdminRegisterSerializer,LoginSerializer, PasswordResetRequestSerializer, PrescriptionMedicineSerializer, PrescriptionMedicineSerializer, PrescriptionTestSerializer, SetNewPasswordSerializer, PatientProfileSerializer, ChangePasswordSerializer, PatientAppointmentSerializer, PrescriptionSerializer

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken # type: ignore
from hospital.models import Hospital_Information, Patient, User 
from doctor.models import Doctor_Information, Appointment, Prescription, Prescription_medicine, Prescription_test
from hospital_admin.models import Admin_Information
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string

@api_view(['GET'])
def getRoutes(request):
    # Specify which urls (routes) to accept
    
    routes = [
        # to test built-in authentication - JSON web tokens have an expiration date
        {'POST': '/api/users/token'},
        {'POST': '/api/users/token/refresh'},

        {'patient_register': '/api/patient_register'},
        {'doctor_register': '/api/doctor_register'},
        {'admin_register': '/api/admin_register'},

        {'login': '/api/login'},
        {'logout': '/api/logout'},

        {'password_reset': '/api/password_reset'},
        {'reset_password_confirm': '/api/reset_password_confirm'},

        {'change_password': '/api/change_password'},

        {'hospitals': '/api/hospital/'},
        {'hospital': '/api/hospital/id'},

        {'doctors': '/api/doctor/'},
        {'doctor': '/api/doctor/id'},

        {'patient_profile': '/api/patient_profile/id'},

        {'appointment': '/api/appointment'},
        {'prescription': '/api/prescription'},
        {'prescription_medicine': '/api/prescription_medicine'},
        {'prescription_test': '/api/prescription_test'},
        {'all_prescription_data': '/api/all_prescription_data'},

    ]
    return Response(routes)

class PatientRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = PatientRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        Patient.objects.create(user=user)

class DoctorRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = DoctorRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        Doctor_Information.objects.create(user=user)

class AdminRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        Admin_Information.objects.create(user=user)

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


reset_tokens = {}  # عشان نحتفظ بالتوكن بشكل مؤقت
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'] # type: ignore
            try:
                user = User.objects.get(email=email)
                token = get_random_string(50)
                reset_tokens[email] = token

                # Send Email
                reset_link = f"http://127.0.0.1:8000/api/reset_password_confirm/?email={email}&token={token}"
                send_mail(
                    'Password Reset Request',
                    f'Click here to reset your password: {reset_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )

                return Response({'message': 'Password reset link sent to email.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = request.query_params.get('email')
            token = serializer.validated_data['token'] # type: ignore

            if email not in reset_tokens or reset_tokens[email] != token:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
                user.set_password(serializer.validated_data['password']) # type: ignore
                user.save()
                del reset_tokens[email]  # احذف التوكن بعد التغيير

                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self): # type: ignore
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = self.get_object()
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        access_token = request.headers.get("Authorization","").split("Bearer ")[-1]
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken(refresh_token)
        refresh.blacklist()

        try:
            # if access_token:
            access = AccessToken(access_token)
            print(access_token)
            print(access)
            access.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token or already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)


#################################################################################################################################

class getHospitals(generics.ListAPIView):
    queryset = Hospital_Information.objects.all()
    serializer_class = HospitalSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class GetOneHospital(generics.RetrieveAPIView):
    queryset = Hospital_Information.objects.all()
    serializer_class = HospitalSerializer
    lookup_field = 'pk'
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

class GetDoctors(generics.ListAPIView):
    queryset = Doctor_Information.objects.all()
    serializer_class = DoctorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

class GetOneDoctor(generics.RetrieveAPIView):
    queryset = Doctor_Information.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'pk'
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

# class PatientProfiles(generics.ListAPIView):
    # queryset = Patient.objects.all()
    # serializer_class = PatientProfileSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [AllowAny]

class PatientProfile(generics.RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientProfileSerializer
    lookup_field = 'pk'
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

class PatientAppointment(generics.ListCreateAPIView):
    # user = request.user
    queryset = Appointment.objects.all()
    serializer_class = PatientAppointmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(patient__user=self.request.user)

    def perform_create(self,serializer):
        user = self.request.user
        print(user)
        patient_data = Patient.objects.get(user=user)
        serializer.save(
            patient = patient_data,
            appointment_status = "pending",
            payment_status = "pending",
            serial_number = str(uuid.uuid4())[:8] ,
        )

class PatientPrescription(generics.ListAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prescription.objects.filter(patient__user=self.request.user)

class PatientPrescriptionMedicine(generics.ListAPIView):
    queryset = Prescription_medicine.objects.all()
    serializer_class = PrescriptionMedicineSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prescription_medicine.objects.filter(prescription__patient__user=self.request.user)

class PatientPrescriptionTest(generics.ListAPIView):
    queryset = Prescription_test.objects.all()
    serializer_class = PrescriptionTestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prescription_test.objects.filter(prescription__patient__user=self.request.user)
    

class CombinedDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        prescriptions = Prescription.objects.filter(patient__user=user)
        prescriptions_medicine = Prescription_medicine.objects.filter(prescription__patient__user=user)
        prescriptions_test = Prescription_medicine.objects.filter(prescription__patient__user=user)

        # استخدام Serializer لتحويل البيانات إلى JSON
        data = {
            "prescriptions": PrescriptionSerializer(prescriptions, many=True).data,
            "prescriptions_medicine": PrescriptionMedicineSerializer(prescriptions_medicine, many=True).data,
            "prescriptions_test": PrescriptionTestSerializer(prescriptions_test, many=True).data,
        }

        return Response(data)
