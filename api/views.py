from django.http import JsonResponse
from .models import *
from .utils import *
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


def RecruiterJAF(request,form_id=None):
    if(request.method=='GET'):
        
        # if not request.user.is_authenticated:
        #     return JsonResponse({'error': 'Please login first'}, status=400)
        
        # # logic to determine that user is logged in as recruiter
        # if request.user.role != 'recruiter':
        #     return JsonResponse({'error': 'Please login as recruiter'}, status=400)
        
        # email = request.user.email
        email="2020csb1068@oracle.com"

        if( User.objects.filter(email=email).exists() == False):
            return JsonResponse({'error': 'Recruiter is not present on portal'}, status=400)

        organisation_name=User.objects.get(email=email).company_name


        # if request contains a form id, then return that form
        if form_id is not None:
            JAF_Form = JAFForm.objects.filter(id=form_id).first()

            if not JAF_Form:
                return JsonResponse({'error': 'Invalid form id'}, status=400)
            
            return JsonResponse({'JAF_form': JAF_Form}, status=200)
            
        JAF_FormList = JAFForm.objects.filter(organisation_name=organisation_name).values('id', 'timestamp', 'is_draft')
        return JsonResponse({'JAF_list': list(JAF_FormList)}, status=200)

def RecruiterSubmitJAF(request,form_id=None):
    if(request.method=="GET"):

        # if not request.user.is_authenticated:
        #     return JsonResponse({'error': 'Please login first'}, status=400)
        
        # # logic to determine that user is logged in as recruiter
        # if request.user.role != 'recruiter':
        #     return JsonResponse({'error': 'Please login as recruiter'}, status=400)
        
        if not request.body:
            return JsonResponse({'error': 'Please provide JAF form Info'}, status=400)

        data = json.loads(request.body)

        save_as_draft = data.get('save_as_draft', None)
        form_data = data.get('form_data', None)

        if form_data:
            JAF_Form=None
            if( form_id is None):
                JAF_Form = JAFForm.objects.create(
                    organisation_name = form_data.get('organisation_name', None),
                    organisation_postal_address = form_data.get('organisation_postal_address', None),
                    organisation_website = form_data.get('organisation_website', None),
                    organisation_type_options = form_data.get('organisation_type_options', None),
                    organisation_type_others = form_data.get('organisation_type_others', None),
                    industry_sector_options = form_data.get('industry_sector_options', None),
                    industry_sector_others = form_data.get('industry_sector_others', None),
                    job_profile_designation = form_data.get('job_profile_designation', None),
                    job_profile_job_description = form_data.get('job_profile_job_description', None),
                    job_profile_job_description_pdf = form_data.get('job_profile_job_description_pdf', None),
                    job_profile_place_of_posting = form_data.get('job_profile_place_of_posting', None),

                    is_draft = save_as_draft, 
                    timestamp = timezone.now(),
                    
                    contact_details_head_hr = AddContactDetails(form_data['contact_details_head_hr']),
                    contact_details_first_person_of_contact = AddContactDetails(form_data['contact_details_first_person_of_contact']),
                    contact_details_second_person_of_contact = AddContactDetails(form_data['contact_details_second_person_of_contact']),
                    salary_details_b_tech = AddSalaryDetails(form_data['salary_details_b_tech']),
                    salary_details_m_tech = AddSalaryDetails(form_data['salary_details_m_tech']),
                    salary_details_m_sc = AddSalaryDetails(form_data['salary_details_m_sc']),
                    salary_details_phd = AddSalaryDetails(form_data['salary_details_phd']),
                    selection_process = AddSelectionProcess(form_data['selection_process'])
                )
            elif JAFForm.objects.filter(id=form_id).exists:
                JAF_Form=JAFForm.objects.get(id=form_id)
                JAF_Form.organisation_name = form_data.get('organisation_name', None)
                JAF_Form.organisation_postal_address = form_data.get('organisation_postal_address', None)
                JAF_Form.organisation_website = form_data.get('organisation_website', None)
                JAF_Form.organisation_type_options = form_data.get('organisation_type_options', None)
                JAF_Form.organisation_type_others = form_data.get('organisation_type_others', None)
                JAF_Form.industry_sector_options = form_data.get('industry_sector_options', None)
                JAF_Form.industry_sector_others = form_data.get('industry_sector_others', None)
                JAF_Form.job_profile_designation = form_data.get('job_profile_designation', None)
                JAF_Form.job_profile_job_description = form_data.get('job_profile_job_description', None)
                JAF_Form.job_profile_job_description_pdf = form_data.get('job_profile_job_description_pdf', None)
                JAF_Form.job_profile_place_of_posting = form_data.get('job_profile_place_of_posting', None)

                JAF_Form.is_draft = save_as_draft
                JAF_Form.timestamp = timezone.now()
                
                JAF_Form.contact_details_head_hr = AddContactDetails(form_data['contact_details_head_hr'])
                JAF_Form.contact_details_first_person_of_contact = AddContactDetails(form_data['contact_details_first_person_of_contact'])
                JAF_Form.contact_details_second_person_of_contact = AddContactDetails(form_data['contact_details_second_person_of_contact'])
                JAF_Form.salary_details_b_tech = AddSalaryDetails(form_data['salary_details_b_tech'])
                JAF_Form.salary_details_m_tech = AddSalaryDetails(form_data['salary_details_m_tech'])
                JAF_Form.salary_details_m_sc = AddSalaryDetails(form_data['salary_details_m_sc'])
                JAF_Form.salary_details_phd = AddSalaryDetails(form_data['salary_details_phd'])
                JAF_Form.selection_process = AddSelectionProcess(form_data['selection_process'])
            
                JAF_Form.save()
            else:
                return JsonResponse({'error': 'Invalid form id'}, status=400) 
            


            if form_id is None:
                return JsonResponse({'success': 'JAF form created successfully'}, status=200)
            else:
                return JsonResponse({'success': 'JAF form updated successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Please provide JAF form data'}, status=400)

def RecruiterINF(request,form_id=None):
    if( request.method=='GET'):

        # if not request.user.is_authenticated:
        #     return JsonResponse({'error': 'Please login first'}, status=400)
        
        # if request.user.role != 'recruiter':
        #     return JsonResponse({'error': 'Please login as recruiter'}, status=400)
        
        # email = request.user.email
        email="2020csb1068@oracle.com"

        if( User.objects.filter(email=email).exists() == False):
            return JsonResponse({'error': 'Recruiter is not present on portal'}, status=400)
        
        organisation_name = User.objects.get(email=email).company_name

        # if request contains a form id, then return that form
        if form_id is not None:
            INF_Form = INFForm.objects.filter(id=form_id).first()

            if not INF_Form:
                return JsonResponse({'error': 'Invalid form id'}, status=400)

            return JsonResponse({'INF_form': INF_Form}, status=200)
            
        INF_FormList = INFForm.objects.filter(organisation_name=organisation_name).values('id', 'timestamp', 'is_draft')
        return JsonResponse({'INF_list': list(INF_FormList)}, status=200)

def RecruiterSubmitINF(request,form_id=None):
    if(request.method=="POST"):

        # if not request.user.is_authenticated:
        #     return JsonResponse({'error': 'Please login first'}, status=400)
        
        # # logic to determine that user is logged in as recruiter
        # if request.user.role != 'recruiter':
        #     return JsonResponse({'error': 'Please login as recruiter'}, status=400)
        
        if not request.body:
            return JsonResponse({'error': 'Please provide INF form Info'}, status=400)

        data = json.loads(request.body)
        save_as_draft = data.get('save_as_draft', None)
        form_data = data.get('form_data', None)

        if form_data:
            INF_Form=None
            if( form_id is None):
                INF_Form = INFForm.objects.create(
                    organisation_name=form_data.get('organisation_name', None),
                    organisation_postal_address=form_data.get('organisation_postal_address', None),
                    organisation_website=form_data.get('organisation_website', None),
                    organisation_type_options=form_data.get('organisation_type_options', None),
                    organisation_type_others=form_data.get('organisation_type_others', None),
                    industry_sector_options=form_data.get('industry_sector_options', None),
                    industry_sector_others=form_data.get('industry_sector_others', None),
                    job_profile_designation=form_data.get('job_profile_designation', None),
                    job_profile_job_description=form_data.get('job_profile_job_description', None),
                    job_profile_job_description_pdf=form_data.get('job_profile_job_description_pdf', None),
                    job_profile_place_of_posting=form_data.get('job_profile_place_of_posting', None),

                    is_draft=save_as_draft,
                    timestamp=timezone.now(),

                    job_profile_six_months_intern=form_data.get('job_profile_six_months_intern', None),
                    job_profile_two_months_intern=form_data.get('job_profile_two_months_intern', None),
                    job_profile_joint_master_thesis_program=form_data.get('job_profile_joint_master_thesis_program', None),
                    
                    contact_details_head_hr=AddContactDetails(form_data.get('contact_details_head_hr', None)),
                    contact_details_first_person_of_contact=AddContactDetails(form_data.get('contact_details_first_person_of_contact', None)),
                    contact_details_second_person_of_contact=AddContactDetails(form_data.get('contact_details_second_person_of_contact', None)),
                    stipend_details_stipend_amount=form_data.get('stipend_details_stipend_amount', None),
                    stipend_details_bonus_perks_incentives=form_data.get('stipend_details_bonus_perks_incentives', None),
                    stipend_details_accodation_trip_fare=form_data.get('stipend_details_accodation_trip_fare', None),
                    stipend_details_bonus_service_contract=form_data.get('stipend_details_bonus_service_contract', None),
                    selection_process=AddSelectionProcess(form_data.get('selection_process', None))
                )
            elif INFForm.objects.filter(id=form_id).exists:
                INF_Form=INFForm.objects.get(id=form_id)
                INF_Form.organisation_name=form_data.get('organisation_name', None)
                INF_Form.organisation_postal_address=form_data.get('organisation_postal_address', None)
                INF_Form.organisation_website=form_data.get('organisation_website', None)
                INF_Form.organisation_type_options=form_data.get('organisation_type_options', None)
                INF_Form.organisation_type_others=form_data.get('organisation_type_others', None)
                INF_Form.industry_sector_options=form_data.get('industry_sector_options', None)
                INF_Form.industry_sector_others=form_data.get('industry_sector_others', None)
                INF_Form.job_profile_designation=form_data.get('job_profile_designation', None)
                INF_Form.job_profile_job_description=form_data.get('job_profile_job_description', None)
                INF_Form.job_profile_job_description_pdf=form_data.get('job_profile_job_description_pdf', None)
                INF_Form.job_profile_place_of_posting=form_data.get('job_profile_place_of_posting', None)

                INF_Form.is_draft=save_as_draft
                INF_Form.timestamp=timezone.now()

                INF_Form.job_profile_six_months_intern=form_data.get('job_profile_six_months_intern', None)
                INF_Form.job_profile_two_months_intern=form_data.get('job_profile_two_months_intern', None)
                INF_Form.job_profile_joint_master_thesis_program=form_data.get('job_profile_joint_master_thesis_program', None)
                
                INF_Form.contact_details_head_hr=AddContactDetails(form_data.get('contact_details_head_hr', None))  
                INF_Form.contact_details_first_person_of_contact=AddContactDetails(form_data.get('contact_details_first_person_of_contact', None))
                INF_Form.contact_details_second_person_of_contact=AddContactDetails(form_data.get('contact_details_second_person_of_contact', None))
                INF_Form.stipend_details_stipend_amount=form_data.get('stipend_details_stipend_amount', None)
                INF_Form.stipend_details_bonus_perks_incentives=form_data.get('stipend_details_bonus_perks_incentives', None)
                INF_Form.stipend_details_accodation_trip_fare=form_data.get('stipend_details_accodation_trip_fare', None)
                INF_Form.stipend_details_bonus_service_contract=form_data.get('stipend_details_bonus_service_contract', None)
                INF_Form.selection_process=AddSelectionProcess(form_data.get('selection_process', None))
                
                INF_Form.save()
            else:
                return JsonResponse({'error': 'Invalid form id'}, status=400)

            if form_id is None:
                return JsonResponse({'success': 'INF form created successfully'}, status=200)
            else:
                return JsonResponse({'success': 'INF form updated successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Please provide INF form Data'}, status=400)
        

# API Working
def SpocDetails(request):

    if(request.method=='GET'):
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login first'}, status=400)
        
        # logic to determine that user is logged in as recruiter
        if request.user.role != 'recruiter':
            return JsonResponse({'error': 'Please login as recruiter'}, status=400)
        
        email = request.session['email']

        # email="2020csb1068@oracle.com"

        spoc_info = SpocCompany.objects.filter(HREmail=email).first()
        
        if not spoc_info:
            return JsonResponse({'Info': 'No Spoc is currently assigned'}, status=200)
        
        if( User.objects.filter(email=spoc_info.spocEmail).exists() == False):
            return JsonResponse({'error': 'Spoc is not present on portal'}, status=400)
        
        spoc_details = User.objects.get(email=spoc_info.spocEmail)


        return JsonResponse({'Name':spoc_details.name,'Phone': spoc_details.phone,"Email":spoc_details.email}, status=200)

# API Working   
def DepartmentPrograms(request,degree):
    if request.method=="GET":
        if degree is not None:
            branch = InterestedDiscipline.objects.filter(degree=degree).values('branch')
            return JsonResponse({'branch': list(branch)}, status=200)
        else:
            return JsonResponse({'error': 'Please provide degree'}, status=400)
        