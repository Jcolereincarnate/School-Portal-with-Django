from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *;
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from . import backends
from django.http import HttpResponse
import requests
from datetime import datetime
from django.template.loader import get_template
from django.http import HttpResponse

@login_required
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'registration/login.html')
User = get_user_model()
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') 
        password = request.POST.get('password')

        try:
            # Get the user object tied to this matric number
           student = StudentProfile.objects.get(matric_number=username)
           user = authenticate(request, username=username, password=password)
        except StudentProfile.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid matric number or password')

    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        matric_number = request.POST.get('matric_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
            
        if User.objects.filter(username=matric_number).exists():
            messages.error(request, 'Matric number already registered')
            return redirect('register')
            
        user = User.objects.create_user(
            username=matric_number,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        profile = StudentProfile.objects.create(
            user=user,
            matric_number=matric_number,
            phone_number=request.POST.get('phone_number'),
            department=request.POST.get('department'),
            level=request.POST.get('level'),
            address=request.POST.get('address', ''),
            profile_picture=request.FILES.get('profile_picture'),
            gender = request.POST.get('gender')
        )
        
        login(request, user)
        messages.success(request, 'Registration successful')
        return redirect('dashboard')
        
    return render(request, 'auth/register.html')

@login_required
def dashboard(request):
    student = request.user.studentprofile
    current_session = SchoolSession.objects.filter(is_active=True).first()
    if current_session:
        session = current_session.session 
        semester = current_session.semester  
    else:
      
        session = '2024/2025' 
        semester = 1  

   
    registered_courses = RegisteredCourse.objects.filter(
        student=student,
        session=session,  
        semester=semester 
    )

  
    recent_results = Result.objects.filter(
        registered_course__student=student
    ).order_by('-registered_course__registration_date')[:5]

 
    fees_paid = Payment.objects.filter(
        student=student,
        purpose='School Fees',
        reference__icontains=session, 
        status='Completed'
    ).exists()

    hostel_status = HostelApplication.objects.filter(
        student=student,
        session=session,
        status='Approved'
    ).first()

  
    total_units = registered_courses.aggregate(Sum('course__units'))['course__units__sum'] or 0

  
    context = {
        'current_session': session,  
        'current_semester': semester, 
        'registered_courses_count': registered_courses.count(),
        'total_units': total_units,
        'recent_results': recent_results,
        'fees_paid': fees_paid,
        'hostel_status': hostel_status,
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def profile(request):
    return render(request, 'portal/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        student = request.user.studentprofile
        student.phone_number = request.POST.get('phone_number')
        student.address = request.POST.get('address')
        
        if 'profile_picture' in request.FILES:
            student.profile_picture = request.FILES['profile_picture']
            
        student.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
        
    return render(request, 'portal/edit_profile.html')

@login_required
def course_registration(request):
    student = request.user.studentprofile
    current_session = SchoolSession.objects.filter(is_active=True).first()
    if current_session:
        session = current_session.session  
        semester = current_session.semester  
    else:
       
        session = '2023/2024' 
        semester = 1 

    
    available_courses = Course.objects.filter(
        level=student.level,
        semester=semester
    )
    
    registered_courses = RegisteredCourse.objects.filter(
        student=student,
        session=session,
        semester=semester
    )
    
    if request.method == 'POST':
        selected_courses = request.POST.getlist('courses')
        
    
        registered_courses.delete()
        
      
        for course_id in selected_courses:
            course = Course.objects.get(id=course_id)
            RegisteredCourse.objects.create(
                student=student,
                course=course,
                session=current_session,
                semester=semester
            )
            
        messages.success(request, 'Course registration successful')
        return redirect('registered_courses')
    
    context = {
        'available_courses': available_courses,
        'registered_courses': registered_courses,
    }
    
    return render(request, 'portal/course_registration.html', context)

@login_required
def registered_courses(request):
     student = request.user.studentprofile
     current_session = SchoolSession.objects.filter(is_active=True).first()
    
     if current_session:
        session = current_session.session
        semester = current_session.semester
     else:
        session = '2024/2025'
        semester = 1

    
     registered_courses = RegisteredCourse.objects.filter(
        student=student,
        semester = semester,
        session = session,
     ) 

     total_units = registered_courses.aggregate(Sum('course__units'))['course__units__sum'] or 0

     context = {
        'registered_courses': registered_courses,
        'total_units': total_units,
     }

     return render(request, 'portal/registered_course.html', context)

@login_required
def results(request):
    student = request.user.studentprofile
    results = Result.objects.filter(
        registered_course__student=student
    ).order_by('-registered_course__registration_date')
    
    context = {
        'results': results,
    }
    print(results)
    
    return render(request, 'portal/results.html', context)

@login_required
def print_results(request):
    student = request.user.studentprofile
    results = Result.objects.filter(
        registered_course__student=student
    ).order_by('-registered_course__registration_date')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    

    p.drawString(100, 750, f"Results for {student.user.get_full_name()}")
    p.drawString(100, 730, f"Matric Number: {student.matric_number}")
    
    y = 700
    for result in results:
        course = result.registered_course.course
        p.drawString(100, y, f"{course.code} - {course.title}")
        p.drawString(400, y, f"Grade: {result.grade}")
        y -= 20
        
    p.showPage()
    p.save()
    
  
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="results_{student.matric_number}.pdf"'
    response.write(pdf)
    
    return response

@login_required
def payments(request):
    student = request.user.studentprofile
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        purpose = request.POST.get('purpose')
        
        # Initialize Remita payment
        # This is a placeholder - actual Remita integration would go here
        payment = Payment.objects.create(
            student=student,
            purpose=purpose,
            amount=amount,
            reference=f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status='Pending'
        )
        
        # Redirect to Remita payment page
        return redirect('payment_process')
    
    return render(request, 'portal/payment.html')

@login_required
def payment_history(request):
    student = request.user.studentprofile
    payments = Payment.objects.filter(student=student).order_by('-transaction_date')
    
    context = {
        'payments': payments,
    }
    
    return render(request, 'payment/history.html', context)

@login_required
def hostel_application(request):
    student = request.user.studentprofile
    current_session = '2024/2025'
    
    existing_application = HostelApplication.objects.filter(
        student=student,
        session=current_session
    ).first()
    
    available_hostels = Hostel.objects.filter(
        gender= student.gender,
        occupied__lt=models.F('capacity')
    )
    
    if request.method == 'POST':
        hostel_id = request.POST.get('hostel')
        hostel = Hostel.objects.get(id=hostel_id)
        
        application = HostelApplication.objects.create(
            student=student,
            hostel=hostel,
            session=current_session
        )

        print(available_hostels)
        
        messages.success(request, 'Hostel application submitted successfully')
        return redirect('dashboard')
    
    context = {
        'current_session': current_session,
        'existing_application': existing_application,
        'available_hostels': available_hostels,
    }
    
    return render(request, 'portal/application.html', context)

@login_required
def notifications(request):
    student = request.user.studentprofile
    notifications = Notification.objects.filter(student=student).order_by('-created_at')
    
 
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'portal/base.html', context)