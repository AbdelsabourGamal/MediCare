from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from .forms import DoctorUserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from hospital.models import User, Patient
from .models import Doctor_Information, Appointment, Education, Experience, Prescription_medicine, Report,Specimen,Test, Prescription_test, Prescription, Doctor_review
from hospital_admin.models import Test_Information
from django.db.models import Q, Count
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import random
import string
from datetime import datetime, timedelta
import datetime
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.html import strip_tags
from io import BytesIO
from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Report
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def generate_random_string():
    N = 8
    string_var = ""
    string_var = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=N))
    return string_var

@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def doctor_change_password(request,pk):
    doctor = Doctor_Information.objects.get(user_id=pk)
    user = User.objects.get(username=doctor.username)
    context={'doctor':doctor}
    if request.method == "POST":
        old_password = request.POST["old_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if check_password(old_password, user.password):
            if new_password == confirm_password:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request,"Password Changed Successfully")
                return redirect("doctor:doctor-login")

            else:
                messages.error(request,"New Password and Confirm Password is not same")
                return redirect("doctor:doctor-change-password",pk)
        else:
            messages.error(request,"Old Password Is Not Correct")
            return redirect("doctor:doctor-change-password",pk)

    return render(request, 'doctor-change-password.html',context)

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutDoctor(request):
    user = User.objects.get(id=request.user.id)
    if user.is_doctor:
        user.save()
        logout(request)

    messages.success(request, 'User Logged out')
    return render(request,'doctor-login.html')

@csrf_exempt
def doctor_register(request):
    page = 'doctor-register'
    form = DoctorUserCreationForm()

    if request.method == 'POST':
        form = DoctorUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = user.username
            user.last_name = user.username
            user.is_doctor = True
            user.save()

            messages.success(request, 'Doctor account was created!')

            login(request, user)
            return redirect('doctor:doctor-profile-settings')

        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'doctor-register.html', context)

@csrf_exempt
def doctor_login(request):
    # page = 'patient_login'
    if request.method == 'GET':
        return render(request, 'doctor-login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(username=username, password=password)

        if user is not None:

            login(request, user)
            if request.user.is_doctor:
                # user.login_status = "online"
                # user.save()
                messages.success(request, 'Welcome Doctor!')
                return redirect('doctor:doctor-dashboard')
            else:
                messages.error(request, 'Invalid credentials. Not a Doctor')
                return redirect('doctor:doctor-logout')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'doctor-login.html')

@csrf_exempt
@login_required(login_url="doctor:doctor-login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def doctor_dashboard(request):
        if request.user.is_authenticated:
            if request.user.is_doctor:
                doctor = Doctor_Information.objects.get(user=request.user)
                current_date = datetime.date.today()
                current_date_str = str(current_date)
                today_appointments = Appointment.objects.filter(date=current_date_str).filter(doctor=doctor)

                next_date = current_date + datetime.timedelta(days=1) # next days date
                next_date_str = str(next_date)
                next_days_appointment = Appointment.objects.filter(date=next_date_str).filter(doctor=doctor).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()

                today_patient_count = Appointment.objects.filter(date=current_date_str).filter(doctor=doctor).annotate(count=Count('patient'))
                total_appointments_count = Appointment.objects.filter(doctor=doctor).annotate(count=Count('id'))
            else:
                return redirect('doctor:doctor-logout')

            context = {'doctor': doctor, 'today_appointments': today_appointments, 'today_patient_count': today_patient_count, 'total_appointments_count': total_appointments_count, 'next_days_appointment': next_days_appointment, 'current_date': current_date_str, 'next_date': next_date_str}
            return render(request, 'doctor-dashboard.html', context)
        else:
            return redirect('doctor:doctor-login')


@csrf_exempt
@login_required(login_url="doctor:doctor-login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def appointments(request):
        if request.user.is_authenticated:
            if request.user.is_doctor:
                doctor = Doctor_Information.objects.get(user=request.user)
                total_appointments = Appointment.objects.filter(doctor=doctor).order_by('-id')
            else:
                return redirect('doctor:doctor-login')

            context = {'doctor': doctor, 'total_appointments': total_appointments}
            return render(request, 'appointments.html', context)
        else:
            return redirect('doctor:doctor-login')


@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def accept_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.appointment_status = 'confirmed'
    appointment.save()

    # Mailtrap

    patient_email = appointment.patient.email
    patient_name = appointment.patient.name
    patient_username = appointment.patient.username
    patient_serial_number = appointment.patient.serial_number
    doctor_name = appointment.doctor.name

    appointment_serial_number = appointment.serial_number
    appointment_date = appointment.date
    appointment_time = appointment.time
    appointment_status = appointment.appointment_status

    subject = "Appointment Acceptance Email"

    values = {
            "email":patient_email,
            "name":patient_name,
            "username":patient_username,
            "serial_number":patient_serial_number,
            "doctor_name":doctor_name,
            "appointment_serial_num":appointment_serial_number,
            "appointment_date":appointment_date,
            "appointment_time":appointment_time,
            "appointment_status":appointment_status,
    }

    html_message = render_to_string('appointment_accept_mail.html', {'values': values})
    plain_message = strip_tags(html_message)

    try:
        send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found')

    messages.success(request, 'Appointment Accepted')

    return redirect('doctor:doctor-dashboard')

@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def reject_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.appointment_status = 'cancelled'
    appointment.save()

    # Mailtrap

    patient_email = appointment.patient.email
    patient_name = appointment.patient.name
    doctor_name = appointment.doctor.name

    subject = "Appointment Rejection Email"

    values = {
            "email":patient_email,
            "name":patient_name,
            "doctor_name":doctor_name,
    }

    html_message = render_to_string('appointment_reject_mail.html', {'values': values})
    plain_message = strip_tags(html_message)

    try:
        send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found')

    messages.error(request, 'Appointment Rejected')

    return redirect('doctor:doctor-dashboard')


@csrf_exempt
@login_required(login_url="login")
def doctor_profile(request, pk):
    # request.user --> get logged in user
    if request.user.is_patient:
        patient = request.user.patient
        doctorr = Doctor_Information.objects.get(doctor_id=pk)
        doctor = None
    else:
        doctor = Doctor_Information.objects.get(user=request.user)
        patient = None
        doctorr = Doctor_Information.objects.get(doctor_id=pk)

    educations = Education.objects.filter(doctor=doctorr).order_by('-year_of_completion')
    experiences = Experience.objects.filter(doctor=doctorr).order_by('-from_year','-to_year')
    doctor_review = Doctor_review.objects.filter(doctor=doctorr)

    context = {'doctor': doctor,'doctorr': doctorr, 'patient': patient, 'educations': educations, 'experiences': experiences, 'doctor_review': doctor_review}
    return render(request, 'doctor-profile.html', context)

@csrf_exempt
@login_required(login_url="login")
def doctor_profille(request):
    # request.user --> get logged in user
    if request.user.is_doctor:
        doctorr = Doctor_Information.objects.get(user=request.user)
        doctor = doctorr

    educations = Education.objects.filter(doctor=doctorr).order_by('-year_of_completion')
    experiences = Experience.objects.filter(doctor=doctorr).order_by('-from_year','-to_year')
    doctor_review = Doctor_review.objects.filter(doctor=doctorr)

    context = {'doctor':doctor, 'doctorr': doctorr,'educations': educations, 'experiences': experiences, 'doctor_review': doctor_review}
    return render(request, 'doctor-profile.html', context)

@csrf_exempt
@login_required(login_url="doctor:doctor-login") # type: ignore
def delete_education(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)

        educations = Education.objects.get(education_id=pk)
        educations.delete()

        messages.success(request, 'Education Deleted')
        return redirect('doctor:doctor-profile-settings')

@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def delete_experience(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)

        experiences = Experience.objects.get(experience_id=pk)
        experiences.delete()

        messages.success(request, 'Experience Deleted')
        return redirect('doctor:doctor-profile-settings')

@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def doctor_profile_settings(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        old_featured_image = doctor.featured_image

        if request.method == 'GET':
            educations = Education.objects.filter(doctor=doctor)
            experiences = Experience.objects.filter(doctor=doctor)

            context = {'doctor': doctor, 'educations': educations, 'experiences': experiences}
            return render(request, 'doctor-profile-settings.html', context)
        elif request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_featured_image

            name = request.POST.get('name')
            number = request.POST.get('number')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            description = request.POST.get('description')
            consultation_fee = request.POST.get('consultation_fee')
            report_fee = request.POST.get('report_fee')
            nid = request.POST.get('nid')
            visit_hour = request.POST.get('visit_hour')

            degree = request.POST.getlist('degree')
            institute = request.POST.getlist('institute')
            year_complete = request.POST.getlist('year_complete')
            hospital_name = request.POST.getlist('hospital_name')
            start_year= request.POST.getlist('from')
            end_year = request.POST.getlist('to')
            designation = request.POST.getlist('designation')

            doctor.name = name
            doctor.visiting_hour = visit_hour
            doctor.nid = nid
            doctor.gender = gender
            doctor.featured_image = featured_image
            doctor.phone_number = number
            doctor.consultation_fee = consultation_fee
            doctor.report_fee = report_fee
            doctor.description = description
            doctor.dob = dob

            doctor.save()

            # Education
            for i in range(len(degree)):
                education = Education(doctor=doctor)
                education.degree = degree[i]
                education.institute = institute[i]
                education.year_of_completion = year_complete[i]
                education.save()

            # Experience
            for x in range(len(hospital_name)):
                experience = Experience(doctor=doctor)
                experience.work_place_name = hospital_name[x]
                experience.from_year = start_year[x]
                experience.to_year = end_year[x]
                experience.designation = designation[x]
                experience.save()

            # context = {'degree': degree}
            messages.success(request, 'Profile Updated')
            return redirect('doctor:doctor-dashboard')
    else:
        redirect('doctor:doctor-logout')


@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def booking(request, pk):
    patient = request.user.patient
    doctor = Doctor_Information.objects.get(doctor_id=pk)

    if request.method == 'POST':
        appointment = Appointment(patient=patient, doctor=doctor)
        date = request.POST['appoint_date']
        time = request.POST['appoint_time']
        appointment_type = request.POST['appointment_type']
        message = request.POST['message']

        try:
            hour = int(time)
            if 8 <= hour <= 20:
                transformed_time = f"{hour:02d}:00:00"
            else:
                return HttpResponse("Invalid hour range", status=400)
        except (ValueError, TypeError):
            return HttpResponse("Invalid hour input", status=400)

        appointment.date = date
        appointment.time = transformed_time
        appointment.appointment_status = 'pending'
        appointment.serial_number = generate_random_string()
        appointment.appointment_type = appointment_type
        appointment.message = message

        new_appointment_datetime = datetime.datetime.strptime(f"{date} {transformed_time}", "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        if (new_appointment_datetime - now) < timedelta(hours=3):
            return HttpResponse("You must book an appointment at least 3 hours in advance.", status=400)

        appointment.save()

        if message:
            # Mailtrap
            patient_email = appointment.patient.email
            patient_name = appointment.patient.name
            patient_username = appointment.patient.username
            patient_phone_number = appointment.patient.phone_number
            doctor_name = appointment.doctor.name

            subject = "Appointment Request"

            values = {
                    "email":patient_email,
                    "name":patient_name,
                    "username":patient_username,
                    "phone_number":patient_phone_number,
                    "doctor_name":doctor_name,
                    "message":message,
                }

            html_message = render_to_string('appointment-request-mail.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'hospital_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')


        messages.success(request, 'Appointment Booked')
        return redirect('patient-dashboard')

    context = {'patient': patient, 'doctor': doctor}
    return render(request, 'booking.html', context)

@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def my_patients(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        patients = Patient.objects.filter(appointment__doctor=doctor).distinct()
    else:
        redirect('doctor:doctor-logout')


    context = {'doctor': doctor, 'patients': patients}
    return render(request, 'my-patients.html', context)

@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def patient_profile(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        patient = Patient.objects.get(patient_id=pk)
        appointments = Appointment.objects.filter(doctor=doctor).filter(patient=patient)
        prescription = Prescription.objects.filter(doctor=doctor).filter(patient=patient)
        report = Report.objects.filter(doctor=doctor).filter(patient=patient)
    else:
        redirect('doctor:doctor-logout')
    context = {'doctor': doctor, 'appointments': appointments, 'patient': patient, 'prescription': prescription, 'report': report}
    return render(request, 'patient-profile.html', context)


@csrf_exempt
@login_required(login_url="doctor:doctor-login")
def create_prescription(request,pk):
        if request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            patient = Patient.objects.get(patient_id=pk)
            create_date = datetime.date.today()


            if request.method == 'POST':
                prescription = Prescription(doctor=doctor, patient=patient)
                # print(request.POST)
                test_name= request.POST.getlist('test_name')
                test_description = request.POST.getlist('description')
                medicine_name = request.POST.getlist('medicine_name')
                medicine_quantity = request.POST.getlist('quantity')
                medecine_frequency = request.POST.getlist('frequency')
                medicine_duration = request.POST.getlist('duration')
                medicine_relation_with_meal = request.POST.getlist('relation_with_meal')
                medicine_instruction = request.POST.getlist('instruction')
                extra_information = request.POST.get('extra_information')
                # test_info_id = request.POST.getlist('id')
                test_info_id = [int(x) for x in request.POST.getlist('id') if x.isdigit()]

                prescription.extra_information = extra_information
                prescription.create_date = create_date

                prescription.save()

                for i in range(len(medicine_name)):
                    medicine = Prescription_medicine(prescription=prescription)
                    medicine.medicine_name = medicine_name[i]
                    medicine.quantity = medicine_quantity[i]
                    medicine.frequency = medecine_frequency[i]
                    medicine.duration = medicine_duration[i]
                    medicine.instruction = medicine_instruction[i]
                    medicine.relation_with_meal = medicine_relation_with_meal[i]
                    medicine.save()

                for i in range(len(test_name)):
                    tests = Prescription_test(prescription=prescription)
                    tests.test_name = test_name[i]
                    tests.test_description = test_description[i]
                    if i < len(test_info_id):
                        tests.test_info_id = test_info_id[i]
                        test_info = Test_Information.objects.get(test_id=test_info_id[i])
                        tests.test_info_price = test_info.test_price

                    tests.save()

                messages.success(request, 'Prescription Created')
                return redirect('doctor:patient-profile', pk=patient.patient_id)

        context = {'doctor': doctor,'patient': patient}
        return render(request, 'create-prescription.html',context)


@csrf_exempt
def render_to_pdf(template_src, context_dict={}):
    template=get_template(template_src)
    html=template.render(context_dict)
    result=BytesIO()
    pdf=pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(),content_type="aplication/pdf")
    return None

@csrf_exempt
def report_pdf(request, pk):
 if request.user.is_patient:
    patient = Patient.objects.get(user=request.user)
    report = Report.objects.get(report_id=pk)
    specimen = Specimen.objects.filter(report=report)
    test = Test.objects.filter(report=report)
    # current_date = datetime.date.today()
    context={'patient':patient,'report':report,'test':test,'specimen':specimen}
    pdf=render_to_pdf('report_pdf.html', context)
    if pdf:
        response=HttpResponse(pdf, content_type='application/pdf')
        content="inline; filename=report.pdf"
        # response['Content-Disposition']= content
        return response
    return HttpResponse("Not Found")

@csrf_exempt
@login_required(login_url="login")
def patient_search(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(doctor_id=pk)
        id = int(request.GET['search_query'])
        patient = Patient.objects.get(patient_id=id)
        prescription = Prescription.objects.filter(doctor=doctor).filter(patient=patient)
        context = {'patient': patient, 'doctor': doctor, 'prescription': prescription}
        return render(request, 'patient-profile.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'doctor-login.html')

@csrf_exempt
@login_required(login_url="login")
def doctor_test_list(request):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        tests = Test_Information.objects.all
        context = {'doctor': doctor, 'tests': tests}
        return render(request, 'doctor-test-list.html', context)

    elif request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        tests = Test_Information.objects.all
        context = {'patient': patient, 'tests': tests}
        return render(request, 'doctor-test-list.html', context)

    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'doctor-login.html')


@csrf_exempt
@login_required(login_url="login")
def doctor_view_prescription(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        prescriptions = Prescription.objects.get(prescription_id=pk)
        medicines = Prescription_medicine.objects.filter(prescription=prescriptions)
        tests = Prescription_test.objects.filter(prescription=prescriptions)
        context = {'prescription': prescriptions, 'medicines': medicines, 'tests': tests, 'doctor': doctor}
        return render(request, 'doctor-view-prescription.html', context)

@csrf_exempt
@login_required(login_url="login")
def doctor_view_report(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        report = Report.objects.get(report_id=pk)
        specimen = Specimen.objects.filter(report=report)
        test = Test.objects.filter(report=report)
        context = {'report': report, 'test': test, 'specimen': specimen, 'doctor': doctor}
        return render(request, 'doctor-view-report.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'doctor-login.html')

@csrf_exempt
@login_required(login_url="login")
def doctor_review(request, pk):
    if request.user.is_doctor:
        # doctor = Doctor_Information.objects.get(user_id=pk)
        doctor = Doctor_Information.objects.get(user=request.user)

        doctor_review = Doctor_review.objects.filter(doctor=doctor)

        context = {'doctor': doctor, 'doctor_review': doctor_review}
        return render(request, 'doctor-profile.html', context)

    if request.user.is_patient:
        doctor = Doctor_Information.objects.get(doctor_id=pk)
        patient = Patient.objects.get(user=request.user)

        if request.method == 'POST':
            title = request.POST.get('title')
            message = request.POST.get('message')

            doctor_review = Doctor_review(doctor=doctor, patient=patient, title=title, message=message)
            doctor_review.save()

        context = {'doctor': doctor, 'patient': patient, 'doctor_review': doctor_review}
        return render(request, 'doctor-profile.html', context)
    else:
        logout(request)






