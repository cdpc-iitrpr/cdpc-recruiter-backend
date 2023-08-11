from django.http import JsonResponse
from .models import *
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
                JAF_Form = JAFForm.objects.create()
            elif JAFForm.objects.filter(id=form_id).exists:
                JAF_Form=JAFForm.objects.get(id=form_id)
            else:
                return JsonResponse({'error': 'Invalid form id'}, status=400)
            
            JAF_Form.organisation_name = form_data['organisation_name']
            JAF_Form.organisation_postal_address = form_data['organisation_postal_address']
            JAF_Form.organisation_website = form_data['organisation_website']
            JAF_Form.organisation_type_options = form_data['organisation_type_options']
            JAF_Form.organisation_type_others = form_data['organisation_type_others']
            JAF_Form.industry_sector_options = form_data['industry_sector_options']
            JAF_Form.industry_sector_others = form_data['industry_sector_others']
            JAF_Form.job_profile_designation = form_data['job_profile_designation']
            JAF_Form.job_profile_job_description = form_data['job_profile_job_description']
            JAF_Form.job_profile_job_description_pdf = form_data['job_profile_job_description_pdf']
            JAF_Form.job_profile_place_of_posting = form_data['job_profile_place_of_posting']

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
                INF_Form = INFForm.objects.create()
            elif INFForm.objects.filter(id=form_id).exists:
                INF_Form=INFForm.objects.get(id=form_id)
            else:
                return JsonResponse({'error': 'Invalid form id'}, status=400)

            INF_Form.organisation_name=form_data['organisation_name']
            INF_Form.organisation_postal_address=form_data['organisation_postal_address']
            INF_Form.organisation_website=form_data['organisation_website']
            INF_Form.organisation_type_options=form_data['organisation_type_options']
            INF_Form.organisation_type_others=form_data['organisation_type_others']
            INF_Form.industry_sector_options=form_data['industry_sector_options']
            INF_Form.industry_sector_others=form_data['industry_sector_others']
            INF_Form.job_profile_designation=form_data['job_profile_designation']
            INF_Form.job_profile_job_description=form_data['job_profile_job_description']
            INF_Form.job_profile_job_description_pdf=form_data['job_profile_job_description_pdf']
            INF_Form.job_profile_place_of_posting=form_data['job_profile_place_of_posting']

            INF_Form.is_draft=save_as_draft
            INF_Form.timestamp=timezone.now()

            INF_Form.job_profile_six_months_intern=form_data['job_profile_six_months_intern']
            INF_Form.job_profile_two_months_intern=form_data['job_profile_two_months_intern']
            INF_Form.job_profile_joint_master_thesis_program=form_data['job_profile_joint_master_thesis_program']
            
            INF_Form.contact_details_head_hr=AddContactDetails(form_data['contact_details_head_hr'])  
            INF_Form.contact_details_first_person_of_contact=AddContactDetails(form_data['contact_details_first_person_of_contact'])
            INF_Form.contact_details_second_person_of_contact=AddContactDetails(form_data['contact_details_second_person_of_contact'])
            INF_Form.stipend_details_stipend_amount=form_data['stipend_details_stipend_amount']
            INF_Form.stipend_details_bonus_perks_incentives=form_data['stipend_details_bonus_perks_incentives']
            INF_Form.stipend_details_accodation_trip_fare=form_data['stipend_details_accodation_trip_fare']
            INF_Form.stipend_details_bonus_service_contract=form_data['stipend_details_bonus_service_contract']
            INF_Form.selection_process=AddSelectionProcess(form_data['selection_process'])
            
            INF_Form.save()

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
        


def AddContactDetails(contactInfo):
    contact_details = ContactDetails.objects.create()
    contact_details.name = contactInfo['name']
    contact_details.email = contactInfo['email']
    contact_details.mobile = contactInfo['mobile']
    contact_details.phone = contactInfo['phone']

    contact_details.save()
    return contact_details

def AddSalaryDetails(salaryInfo):
    salary_details = SalaryDetails.objects.create()
    salary_details.ctc_gross = salaryInfo['ctc_gross']
    salary_details.ctc_take_home = salaryInfo['ctc_take_home']
    salary_details.ctc_bonus_perks = salaryInfo['ctc_bonus_perks']
    salary_details.bond_contract = salaryInfo['bond_contract']
    salary_details.save()
    return salary_details

def AddSelectionProcess(selectionProcessInfo):
    selection_process = SelectionProcess.objects.create()
    selection_process.test_type = AddTestType(selectionProcessInfo['test_type'])
    selection_process.save()
    
    selection_process.eligibility_criteria = selectionProcessInfo['eligibility_criteria']
    selection_process.allow_backlog_students = selectionProcessInfo['allow_backlog_students']
    selection_process.test_duration = selectionProcessInfo['test_duration']
    selection_process.likely_topics = selectionProcessInfo['likely_topics']
    selection_process.number_of_rounds = selectionProcessInfo['number_of_rounds']
    selection_process.group_discussion_duration = selectionProcessInfo['group_discussion_duration']
    selection_process.number_of_offers  = selectionProcessInfo['number_of_offers']
    selection_process.preferred_period = selectionProcessInfo['preferred_period']
    selection_process.logistics_requirements = selectionProcessInfo['logistics_requirements']
    selection_process.interested_discipline = AddInterestedDiscipline(selectionProcessInfo['interested_discipline'])

def AddTestType(testTypeInfo):
    test_type = TestType.objects.create()
    test_type.ppt = testTypeInfo['ppt']
    test_type.shortlist_from_resume = testTypeInfo['shortlist_from_resume']
    test_type.written_test = testTypeInfo['written_test']
    test_type.online_test = testTypeInfo['online_test']
    test_type.technical_test = testTypeInfo['technical_test']
    test_type.aptitude_test = testTypeInfo['aptitude_test']
    test_type.psychometric_test = testTypeInfo['psychometric_test']
    test_type.group_discussion = testTypeInfo['group_discussion']
    test_type.personal_interview = testTypeInfo['personal_interview']
    test_type.save()
    return test_type

def AddInterestedDiscipline(interestedDisciplineInfo):
    interested_discipline = InterestedDiscipline.objects.create()
    interested_discipline.degree = interestedDisciplineInfo['degree']
    interested_discipline.branch = interestedDisciplineInfo['branch']
    interested_discipline.save()
    return interested_discipline
