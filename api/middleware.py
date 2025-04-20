from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    API_EXCEPTIONS = [
        '/api/',
        '/api/patient_register/',
        '/api/password_reset/', 
    ]

    def __call__(self, request):

        if not request.path.startswith('/api/'):
            return self.get_response(request)

        if request.path in self.API_EXCEPTIONS:
            return self.get_response(request)

        if request.path in ['/api/login/', '/api/logout/']:
            return self.get_response(request)

        try:
            auth = JWTAuthentication()
            validated_token = auth.get_validated_token(auth.get_raw_token(auth.get_header(request))) # type: ignore
            
            jti = validated_token['jti']
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                return JsonResponse(
                    {'detail': 'This token has been invalidated, please login again'},
                    status=401
                )
                
        except InvalidToken:
            return JsonResponse(
                {'detail': 'Invalid or expired token'},
                status=401
            )
            
        return self.get_response(request)