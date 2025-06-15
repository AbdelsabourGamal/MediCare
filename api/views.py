from django.contrib.auth.tokens import default_token_generator
from datetime import datetime
import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
from rest_framework.response import Response
from .serializers import DoctorSerializer, HospitalSerializer, PatientRegisterSerializer, DoctorRegisterSerializer,LoginSerializer, PasswordResetSerializer, PrescriptionMedicineSerializer, PrescriptionMedicineSerializer, PrescriptionTestSerializer, PatientProfileSerializer, ChangePasswordSerializer, PatientAppointmentSerializer, PrescriptionSerializer, ReportSerializer, PaymentSerializer, HospitalDepartmentSerializer, SpecimenSerializer, TestSerializer

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken # type: ignore
from hospital.models import Hospital_Information, Patient, User
from doctor.models import Doctor_Information, Appointment, Prescription, Prescription_medicine, Prescription_test, Report, Specimen, Test
from paypal.models import Payment
from hospital_admin.models import Admin_Information,Hospital_department
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

@api_view(['GET'])
def getRoutes(request):
    # Specify which urls (routes) to accept

    routes = [
        # to test built-in authentication - JSON web tokens have an expiration date

        {'patient_register': '/api/patient_register'},
        {'doctor_register': '/api/doctor_register'},

        {'login': '/api/login'},
        {'logout': '/api/logout'},

        {'password_reset': '/api/password_reset'},

        {'change_password': '/api/change_password'},

        {'hospitals': '/api/hospital/'},
        {'hospital': '/api/hospital/id'},

        {'doctors': '/api/doctor/'},
        {'doctor': '/api/doctor/id'},

        {'patient_profile': '/api/patient_profile/'},

        {'appointment': '/api/appointment'},
        {'prescription': '/api/prescription'},
        {'prescription_medicine': '/api/prescription_medicine'},
        {'prescription_test': '/api/prescription_test'},
        {'report': '/api/report'},
        {'payment': '/api/payment'},
        {'all_prescription_data': '/api/all_prescription_data'},

        {'hospital_department': '/api/hospital_department'},
    ]
    return Response(routes)

class PatientRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = PatientRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "Patient registered successfully",
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_201_CREATED)

class DoctorRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = DoctorRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "Doctor registered successfully",
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_201_CREATED)

""" AdminRegister
class AdminRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        Admin_Information.objects.create(user=user)
"""

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response({
            "message": "Invalid username or password",
            "code": "400"
        }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'] # type: ignore
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = f"https://127.0.0.1:8000/reset/{uid}/{token}"
            send_mail(
                'Password Reset Request',
                f'Use this link to reset your password: {reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'Password reset link sent.'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error sending email: {e}")
            return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]
                token = AccessToken(access_token)

                outstanding_token, created = OutstandingToken.objects.get_or_create(
                    jti=token['jti'],
                    defaults={
                        'token': str(token),
                        'created_at': datetime.fromtimestamp(token['iat']), # type: ignore
                        'expires_at': datetime.fromtimestamp(token['exp']), # type: ignore
                        'user': request.user
                    }
                )

                BlacklistedToken.objects.get_or_create(token=outstanding_token)

            return Response(
                {"detail": "Successfully logged out and all tokens have been invalidated"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"An error occurred during logout: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
    permission_classes = [IsAuthenticated]

class GetDoctors(generics.ListAPIView):
    queryset = Doctor_Information.objects.all()
    serializer_class = DoctorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class GetOneDoctor(generics.RetrieveAPIView):
    queryset = Doctor_Information.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'pk'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class PatientProfile(generics.RetrieveUpdateAPIView):
    serializer_class = PatientProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self): # type: ignore
        return Patient.objects.get(user=self.request.user)

class PatientAppointment(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = PatientAppointmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # type: ignore
        return Appointment.objects.filter(patient__user=self.request.user)

    def perform_create(self,serializer):
        user = self.request.user
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

    def get_queryset(self): # type: ignore
        return Prescription.objects.filter(patient__user=self.request.user)

class PatientPrescriptionMedicine(generics.ListAPIView):
    queryset = Prescription_medicine.objects.all()
    serializer_class = PrescriptionMedicineSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # type: ignore
        return Prescription_medicine.objects.filter(prescription__patient__user=self.request.user)

class PatientPrescriptionTest(generics.ListAPIView):
    queryset = Prescription_test.objects.all()
    serializer_class = PrescriptionTestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # type: ignore
        return Prescription_test.objects.filter(prescription__patient__user=self.request.user)

class PatientReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        report = Report.objects.filter(patient__user=user)
        specimen = Specimen.objects.filter(report__patient__user=user)
        test = Test.objects.filter(report__patient__user=user)

        data = {
            "report": ReportSerializer(report, many=True).data,
            "specimen": SpecimenSerializer(specimen, many=True).data,
            "test": TestSerializer(test, many=True).data
        }

        return Response(data)

class PatientPayment(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # type: ignore
        return Report.objects.filter(patient__user=self.request.user)

class CombinedDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        prescriptions = Prescription.objects.filter(patient__user=user)
        prescriptions_medicine = Prescription_medicine.objects.filter(prescription__patient__user=user)
        prescriptions_test = Prescription_test.objects.filter(prescription__patient__user=user)

        data = {
            "prescriptions": PrescriptionSerializer(prescriptions, many=True).data,
            "prescriptions_medicine": PrescriptionMedicineSerializer(prescriptions_medicine, many=True).data,
            "prescriptions_test": PrescriptionTestSerializer(prescriptions_test, many=True).data
        }

        return Response(data)

class HospitalDepartment(generics.ListAPIView):
    queryset = Hospital_department.objects.all()
    serializer_class = HospitalDepartmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]