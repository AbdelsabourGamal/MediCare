from django.contrib import admin

# Register your models here.
from .models import Admin_Information, Clinical_Laboratory_Technician, Hospital_department, Specialization, Service ,Test_Information

admin.site.register(Admin_Information)

admin.site.register(Clinical_Laboratory_Technician)

admin.site.register(Hospital_department)

admin.site.register(Specialization)

admin.site.register(Service)

admin.site.register(Test_Information)
