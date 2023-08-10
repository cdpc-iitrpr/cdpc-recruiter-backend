from django.http import JsonResponse
from .models import User,JAFForm,SpocCompany
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
        name = data.get('name', None)
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
            request.session['name'] = name
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
                    name=request.session['name'],
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

@authenticate
def RecruiterJAF(request):
    if(request.method=='GET'):
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login first'}, status=400)
        
        # logic to determine that user is logged in as recruiter
        if request.user.role != 'recruiter':
            return JsonResponse({'error': 'Please login as recruiter'}, status=400)
        
        email = request.session['email']
        organisation_name = User.objects.get(email=email).company_name

        # if request contains a form id, then return that form
        if 'form_id' in request.GET:
            JAF_Form = JAFForm.objects.get(id=request.GET['form_id'])
            return JsonResponse({'JAF_form': JAF_Form}, status=200)
            
        JAF_FormList = JAFForm.objects.filter(organisation_name=organisation_name).values('id', 'timestamp', 'is_draft')
        return JsonResponse({'JAF_list': list(JAF_FormList)}, status=200)

@authenticate
def RecruiterSubmitJAF(request):
    if(request.method=="POST"):

        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login first'}, status=400)
        
        # logic to determine that user is logged in as recruiter
        if request.user.role != 'recruiter':
            return JsonResponse({'error': 'Please login as recruiter'}, status=400)
        
        if not request.body:
            return JsonResponse({'error': 'Please provide JAF form'}, status=400)

        data = json.loads(request.body)
        form_id = data.get('form_id', None)
        save_as_draft = data.get('save_as_draft', None)
        form_data = data.get('form_data', None)

        # check if form_id is present in JAFForm table
        if form_id and form_data:
            if JAFForm.objects.filter(id=form_id).exists():
                JAF_Form = JAFForm.objects.get(id=form_id)
                JAF_Form.organisation_name = form_data['organisation_name']
                JAF_Form.organisation_postal_address = form_data['organisation_postal_address']
                JAF_Form.organisation_website = form_data['organisation_website']
                JAF_Form.organisation_type_options = form_data['organisation_type_options']
                JAF_Form.organisation_type_others = form_data['organisation_type_others']
                JAF_Form.industry_sector_options = form_data['industry_sector_options']
                JAF_Form.industry_sector_others = form_data['industry_sector_others']
                JAF_Form.contact_details_head_hr = form_data['contact_details_head_hr']
                JAF_Form.contact_details_first_person_of_contact = form_data['contact_details_first_person_of_contact']
                JAF_Form.contact_details_second_person_of_contact = form_data['contact_details_second_person_of_contact']
                JAF_Form.job_profile_designation = form_data['job_profile_designation']
                JAF_Form.job_profile_job_description = form_data['job_profile_job_description']
                JAF_Form.job_profile_job_description_pdf = form_data['job_profile_job_description_pdf']
                JAF_Form.job_profile_place_of_posting = form_data['job_profile_place_of_posting']
                JAF_Form.salary_details_b_tech = form_data['salary_details_b_tech']
                JAF_Form.salary_details_m_tech = form_data['salary_details_m_tech']
                JAF_Form.salary_details_m_sc = form_data['salary_details_m_sc']
                JAF_Form.salary_details_phd = form_data['salary_details_phd']
                JAF_Form.selection_process = form_data['selection_process']
                JAF_Form.is_draft = save_as_draft
                JAF_Form.save()
                return JsonResponse({'success': 'JAF form updated successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid form id'}, status=400)

@authenticate
def SpocDetails(request):

    if(request.method=='GET'):
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login first'}, status=400)
        
        # logic to determine that user is logged in as recruiter
        if request.user.role != 'recruiter':
            return JsonResponse({'error': 'Please login as recruiter'}, status=400)
        
        email = request.session['email']
        spoc_email=SpocCompany.objects.get(HREmail=email).spocEmail

        if not spoc_email:
            return JsonResponse({'Info': 'No Spoc is currently assigned'}, status=200)
        
        spoc_details = User.objects.get(email=spoc_email)

        return JsonResponse({'Name':spoc_details.name,'Phone': spoc_details.phone,"Email":spoc_details.email}, status=200)
    
def DepartmentPrograms(request):
    if request.method=="GET":
        if 'program' in request.GET:
            departments = DepartmentPrograms.objects.filter(program=request.GET['program']).values('department')
            return JsonResponse({'departments': list(departments)}, status=200)
        else:
            return JsonResponse({'error': 'Please provide program'}, status=400)