from django.http import JsonResponse
from .models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import json
import re
import pyotp


def send_otp(reason, otp_code, email):
    subject = 'OTP for {reason} {otp_code}'.format(reason=reason, otp_code=otp_code)
    message = '''
    Hi,
    Your OTP for {reason} is {otp_code}. This OTP is valid for 5 minutes only.
    Please do not share this OTP with anyone.
    
    Regards,
    CDPC Recruiter Portal
    IIT Ropar
    '''.format(reason=reason, otp_code=otp_code)
    
    receipend_list = [email]
    from_email = settings.EMAIL_HOST_USER
    email_message = EmailMessage(subject, message, from_email, receipend_list)
    if email_message.send(fail_silently=False):
        return True
    else:
        return False

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
        
        
        if send_otp('signup', otp_code, email):
            # Save user info in session
            request.session['email'] = email
            request.session['secret_key'] = secret_key
            request.session['first_name'] = first_name
            request.session['phone'] = phone
            request.session['role'] = role
            request.session['company_name'] = company_name
            request.session['signup'] = True
            return JsonResponse({'success': 'OTP sent to your email'}, status=200)
        else:
            return JsonResponse({'error': 'Unable to send OTP'}, status=400)

@csrf_exempt
def signin(request):
    data = json.loads(request.body)
    email = data.get('email', None)
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not email or not re.match(email_pattern, email):
        return JsonResponse({'error': 'Please provide a valid email'}, status=400)
    if not User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'User does not exist'}, status=400)
    
    #Send OTP to the email
    secret_key = pyotp.random_base32()
    otp = pyotp.TOTP(secret_key, interval=300)
    otp_code = otp.now()
    
    if send_otp('login', otp_code, email):
        # Save user info in session
        request.session['email'] = email
        request.session['secret_key'] = secret_key
        request.session['login'] = True
        return JsonResponse({'success': 'OTP sent to your email'}, status=200)
    else:
        return JsonResponse({'error': 'Unable to send OTP'}, status=400)

@csrf_exempt
def verify(request):
    data = json.loads(request.body)
    otp_code = data.get('otp', None)
    if not otp_code:
        return JsonResponse({'error': 'Please provide OTP'}, status=400)
    if 'signup' in request.session:
        if not request.session['signup']:
            return JsonResponse({'error': 'Please signup first'}, status=400)
    elif 'login' in request.session:
        if not request.session['login']:
            return JsonResponse({'error': 'Please login first'}, status=400)
    else:
        return JsonResponse({'error': 'Please signup or login first'}, status=400)
    
    otp = pyotp.TOTP(request.session['secret_key'], interval=300)
    
    if otp.verify(otp_code):
        if 'signup' in request.session:
            if request.session['signup']:
                # Save user info in database
                if User.objects.filter(email=request.session['email']).exists():
                    return JsonResponse({'error': 'User already exists'}, status=400)
                user = User.objects.create(
                    email=request.session['email'],
                    first_name=request.session['first_name'],
                    phone=request.session['phone'],
                    role=request.session['role'],
                    company_name=request.session['company_name']
                )
                user.save()
                login(request, user)
                del request.session['signup']
                return JsonResponse({'success': 'User created successfully',
                                     'email': user.email,
                                     'role': user.role}, status=200)
        elif 'login' in request.session:
            if request.session['login']:
                # Save user info in database
                user = User.objects.get(email=request.session['email'])
                login(request, user)
                del request.session['login']
                return JsonResponse({'success': 'User logged in successfully',
                                     'email': user.email,
                                     'role': user.role
                                     }, status=200)
    else:
        return JsonResponse({'error': 'Invalid OTP'}, status=400)

def signout(request):
    logout(request)
    return JsonResponse({'success': 'User logged out successfully'}, status=200)