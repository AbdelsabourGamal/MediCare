from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from .serializers import HospitalSerializer
from hospital.models import Hospital_Information, Patient, User 
from doctor.models import Doctor_Information
from rest_framework import generics

@api_view(['GET'])
def getRoutes(request):
    # Specify which urls (routes) to accept
    
    routes = [
        {'hospital': '/api/hospital/'},
        {'GET': '/api/hospital/id'},

        # to test built-in authentication - JSON web tokens have an expiration date
        {'POST': '/api/users/token'},
        {'POST': '/api/users/token/refresh'},
    ]
    return Response(routes)



class getHospitals(generics.ListAPIView):
    model = Hospital_Information
    queryset = Hospital_Information.objects.all()
    serializer_class = HospitalSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class getHospitalProfile(generics.RetrieveAPIView):
    model = Hospital_Information
    queryset = Hospital_Information.objects.all()
    serializer_class = HospitalSerializer
    lookup_field = 'pk'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
