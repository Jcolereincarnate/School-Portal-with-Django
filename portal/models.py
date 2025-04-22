from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matric_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    department = models.CharField(max_length=100)
    level = models.IntegerField(validators=[MinValueValidator(100), MaxValueValidator(800)])
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    @property
    def imageURL(self):
        try:
            url = self.profile_picture.url
        except:
            url =''
        return url

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.matric_number}"

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    units = models.IntegerField()
    level = models.IntegerField()
    semester = models.IntegerField(choices=[(1, 'First'), (2, 'Second')])

    def __str__(self):
        return f"{self.code} - {self.title}"

class RegisteredCourse(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    session = models.CharField(max_length=9) 
    semester = models.IntegerField(choices=[(1, 'First'), (2, 'Second')])
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course', 'session', 'semester']

class Result(models.Model):
    registered_course = models.OneToOneField(RegisteredCourse, on_delete=models.CASCADE)
    ca_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=2, null=True, blank=True, editable=False)

    def calculate_grade(self):
        if self.total_score is None:
            return None
        score = float(self.total_score)
        if score >= 70: return 'A'
        elif score >= 60: return 'B'
        elif score >= 50: return 'C'
        elif score >= 45: return 'D'
        elif score >= 40: return 'E'
        else: return 'F'

    def save(self, *args, **kwargs):
        self.grade = self.calculate_grade()
        super().save(*args, **kwargs)

class Payment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20)
    transaction_date = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=50, null=True, blank=True)

class Hostel(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    capacity = models.IntegerField()
    occupied = models.IntegerField(default=0)
    price_per_bed = models.DecimalField(max_digits=10, decimal_places=2)

class HostelApplication(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    session = models.CharField(max_length=9)
    status = models.CharField(max_length=20, default='Pending')
    application_date = models.DateTimeField(auto_now_add=True)
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True)

class Notification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class SchoolSession(models.Model):
    session = models.CharField(max_length=9)  # e.g. '2023/2024'
    semester = models.IntegerField(choices=[(1, 'First'), (2, 'Second')])
    is_active = models.BooleanField(default=False)  # To mark the current active session

    def __str__(self):
        return f"{self.session}"