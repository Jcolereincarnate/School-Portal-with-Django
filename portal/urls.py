from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('courses/registration/', views.course_registration, name='course_registration'),
    path('courses/registered/', views.registered_courses, name='registered_courses'),
    path('results/', views.results, name='results'),
    path('results/print/', views.print_results, name='print_results'),
    path('payments/', views.payments, name='payments'),
    path('payments/history/', views.payment_history, name='payment_history'),
    path('hostel/', views.hostel_application, name='hostel_application'),
    path('notifications/', views.notifications, name='notifications'),
]