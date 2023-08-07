from django.http import JsonResponse
from .models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
import json
import re
import pyotp

# Create your views here.
@csrf_exempt
def signup(request):
    if request.method == "POST":
        if not request.body:
            return JsonResponse({'error': 'Please provide email'}, status=400)
        data = json.loads(request.body)
        email = data.get('email', None)
        first_name = data.get('name', None)
        phone = data.get('phone', None)
        role = 'recruiter'  # Only recruiter can signup from this API
        company_name = data.get('company_name', None)
        # Validate Email
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not email or not re.match(pattern, email):
            return JsonResponse({'error': 'Please provide a valid email'}, status=400)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'User already exists'}, status=400)
        
        # Send OTP to the email
        secret_key = pyotp.random_base32()
        otp = pyotp.TOTP(secret_key, interval=300)
        otp_code = otp.now()
        
        subject = 'OTP for SIGNUP '+ otp_code
        message = '''
        Hi,
        Your OTP for signup is {otp_code}. This OTP is valid for 5 minutes only.
        Please do not share this OTP with anyone.
        
        Regards,
        CDPC Recruiter Portal
        IIT Ropar
        '''.format(otp_code=otp_code)
        
        receipend_list = [email]
        from_email = settings.EMAIL_HOST_USER
        email_message = EmailMessage(subject, message, from_email, receipend_list)
        if email_message.send(fail_silently=False):
            # Save user info in session
            request.session['email'] = email
            request.session['secret_key'] = secret_key
            request.session['first_name'] = first_name
            request.session['phone'] = phone
            request.session['role'] = role
            request.session['company_name'] = company_name
            
            return JsonResponse({'success': 'OTP sent to your email'}, status=200)
        else:
            return JsonResponse({'error': 'Unable to send OTP'}, status=400)