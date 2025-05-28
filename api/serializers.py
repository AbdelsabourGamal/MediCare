import datetime

from rest_framework import serializers
from hospital.models import Hospital_Information, Patient, User 
from doctor.models import Doctor_Information, Appointment, Prescription, Prescription_medicine, Prescription_test, Report
from hospital_admin.models import Admin_Information,hospital_department
from paypal.models import Payment
from hospital_admin.views import appointment_list
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from django.contrib.auth import authenticate
import uuid

# Serialization --> convert python data (from our database models) to JSON data

class PatientRegisterSerializer(serializers.ModelSerializer):
    is_patient = serializers.BooleanField(default=True, read_only=True)
    serial_number = serializers.CharField(read_only=True)  
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'is_patient','serial_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not validated_data.get(field):
                raise serializers.ValidationError(f"{field} is required.")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.is_patient = True
        user.save()

        serial_number = str(uuid.uuid4())[:8]
        patient = Patient.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            serial_number=serial_number,
        )
        return user

class DoctorRegisterSerializer(serializers.ModelSerializer):
    is_doctor = serializers.BooleanField(default=True, read_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'is_doctor']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not validated_data.get(field):
                raise serializers.ValidationError(f"{field} is required.")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.is_doctor = True
        user.save()

        doctor = Doctor_Information.objects.create(
            user=user,
            username=user.username,
            email=user.email
        )
        return user

"""
class AdminRegisterSerializer(serializers.ModelSerializer):
    is_hospital_admin = serializers.BooleanField(default=True, read_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_hospital_admin','first_name','last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user_data = {
            "username": validated_data.get("username"),
            "email": validated_data.get("email"),
            "password": validated_data.get("password"),
            "first_name": validated_data.get("first_name"),
            "last_name": validated_data.get("last_name")
        }
        user = User.objects.create_user(**user_data)
        user.is_hospital_admin = True
        user.save()

        admin = Admin_Information.objects.create(
            user=user,
            username=user.username,
            email=user.email
        )
        admin.save()
        return user
"""    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data): # type: ignore
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password")

        refresh = RefreshToken.for_user(user)

        return {
            # 'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id, # type: ignore
                'username': user.username,
                'email': user.email,
                "is_doctor": user.is_doctor # type: ignore
            }
        }

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data): # type: ignore
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return data
    
##############################################################################################################

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital_Information
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor_Information
        fields = '__all__'

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class PatientAppointmentSerializer(serializers.ModelSerializer):
    appointment_status = serializers.CharField(default="pending", read_only=True)
    payment_status  = serializers.CharField(default="pending", read_only=True)
    patient = serializers.CharField(default=serializers.CurrentUserDefault(),read_only=True)
    serial_number = serializers.CharField(read_only=True)
    transaction_id = serializers.CharField(read_only=True)
    class Meta:
        model = Appointment
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription_medicine
        fields = '__all__'

class PrescriptionTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription_test
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class CombinedDataSerializer(serializers.Serializer):
    prescriptions = PrescriptionSerializer(many=True)
    prescriptions_medicine = PrescriptionMedicineSerializer(many=True)
    prescriptions_test = PrescriptionTestSerializer(many=True)


class HospitalDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = hospital_department
        fields = '__all__'