from wsgiref.util import FileWrapper
from .models import *
from .utils import *
from django.utils import timezone
from django.contrib.auth import logout
import json
import re
import pyotp
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

@api_view(['POST'])
def signup(request):
    if not request.body:
        return Response({'error': 'Please provide email'}, status=400)
    
    data = json.loads(request.body)
    email = data.get('email', None)
    name = data.get('name', None)
    phone = data.get('phone', None)
    role = 'recruiter' 
    company_name = data.get('company_name', None)

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not email or not re.match(pattern, email):
        return Response({'error': 'Please provide a valid email'}, status=400)
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'User already exists'}, status=400)
    
    secret_key = pyotp.random_base32()
    otp = pyotp.TOTP(secret_key, interval=300)
    otp_code = otp.now()
    
    if send_otp('signup', otp_code, email):
        user = User.objects.create(
            username=email,
            email=email,
            name=name,
            phone=phone,
            role=role,
            company_name=company_name
        )
        user.save()

        user_otp=UserOTP.objects.create(
            email=email,
            secret_key=secret_key
        )
        user_otp.save()
        return Response({'success': 'OTP sent to your email'}, status=200)
    else:
        return Response({'error': 'Unable to send OTP'}, status=400)

@api_view(['POST'])
def signin(request):
    data = json.loads(request.body)
    email = data.get('email', None)
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not email or not re.match(email_pattern, email):
        return Response({'error': 'Please provide a valid email'}, status=400)
    if not User.objects.filter(email=email).exists():
        return Response({'error': 'User does not exist'}, status=400)
    
    secret_key = pyotp.random_base32()
    otp = pyotp.TOTP(secret_key, interval=300)
    otp_code = otp.now()
    
    if send_otp('login', otp_code, email):

        if(UserOTP.objects.filter(email=email).exists()):
            user_otp_obj = UserOTP.objects.get(email=email)
            user_otp_obj.secret_key = secret_key
            user_otp_obj.save()
        else:
            UserOTP.objects.create(
                email=email,
                secret_key=secret_key
            )
            UserOTP.save()

        return Response({'success': 'OTP sent to your email'}, status=200)
    else:
        return Response({'error': 'Unable to send OTP'}, status=400)

@api_view(['POST'])
def verify(request):
    data = json.loads(request.body)
    otp_code = data.get('otp', None)
    email = data.get('email', None)
    if not otp_code:
        return Response({'error': 'Please provide OTP'}, status=400)

    if User.objects.filter(email=email).exists() == False:
        return Response({'error': 'User does not exist'}, status=400)

    user = User.objects.get(email=email)
    user_otp_obj = UserOTP.objects.get(email=email)

    otp = pyotp.TOTP(user_otp_obj.secret_key, interval=300)

    if otp.verify(otp_code):
        token_obj = RefreshToken.for_user(user = user)
        return Response({
            "login": True,
            'refresh':str(token_obj),
            'access':str(token_obj.access_token),
            'user': User.objects.filter(email=email).values('name', 'phone', 'role', 'company_name', 'email', 'role')[0]
        })
    else:
        return Response({'error': 'Invalid OTP'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signout(request):
    try:
        # Get the refresh token from the request header
        refresh_token = request.data.get('refresh_token')

        if refresh_token:
            # Decode the refresh token to get the token object
            token = RefreshToken(refresh_token)
            # Blacklist the token to invalidate it
            token.blacklist()

            return Response({'success': 'User logged out successfully'}, status=200)
        else:
            return Response({'error': 'Refresh token not provided'}, status=400)
    except Exception as e:
        print("Error:", e)
        return Response({'error': 'Error in logging out'}, status=400)

def fileObjectsToJson(fileObjectList):
    files = []
    for fileObject in fileObjectList:
        file = {}
        file['id'] = fileObject.id
        file['file_name'] = fileObject.file_name
        files.append(file)
    return files

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def RecruiterJAF(request,form_id=None):
        
    if request.user.role != 'recruiter':
        return Response({'error': 'Please login as recruiter'}, status=400)
    
    email = request.user.email
    if( User.objects.filter(email=email).exists() == False):
        return Response({'error': 'Recruiter is not present on portal'}, status=400)
    

    if form_id is not None:
        JAF_Form = JAFForm.objects.filter(id=form_id).first()
        if not JAF_Form:
            return Response({'error': 'Invalid form id'}, status=400)
        
        JAF_data = {
            'organisation_name': JAF_Form.organisation_name,
            'organisation_postal_address': JAF_Form.organisation_postal_address,
            'organisation_website': JAF_Form.organisation_website,
            'versionTitle': JAF_Form.versionTitle,
            'organisation_type_options': JAF_Form.organisation_type_options,
            'organisation_type_others': JAF_Form.organisation_type_others,
            'industry_sector_options': JAF_Form.industry_sector_options,
            'industry_sector_others': JAF_Form.industry_sector_others,
            'job_profile_designation': JAF_Form.job_profile_designation,
            'job_profile_job_description': JAF_Form.job_profile_job_description,
            'job_profile_job_description_pdf': fileObjectsToJson(JAF_Form.job_profile_job_description_pdf.all()),
            'job_profile_place_of_posting': JAF_Form.job_profile_place_of_posting,
            'contact_details_head_hr': ObjectToJSON_ContactDetails(JAF_Form.contact_details_head_hr),
            'contact_details_first_person_of_contact': ObjectToJSON_ContactDetails(JAF_Form.contact_details_first_person_of_contact),
            'contact_details_second_person_of_contact': ObjectToJSON_ContactDetails(JAF_Form.contact_details_second_person_of_contact),
            'salary_details_b_tech': ObjectToJSON_SalaryDetails(JAF_Form.salary_details_b_tech),
            'salary_details_m_tech': ObjectToJSON_SalaryDetails(JAF_Form.salary_details_m_tech),
            'salary_details_m_sc': ObjectToJSON_SalaryDetails(JAF_Form.salary_details_m_sc),
            'salary_details_phd': ObjectToJSON_SalaryDetails(JAF_Form.salary_details_phd),
            'selection_process': ObjectToJSON_SelectionProcess(JAF_Form.selection_process)
        } 
        return Response( {"Data": JAF_data}, status=200)
    
    user_email = User.objects.get(email=email)
    JAF_FormList = JAFForm.objects.filter(submitted_by=user_email).values('id', 'timestamp', 'is_draft','versionTitle')
    return Response({'JAF_list': list(JAF_FormList)}, status=200)

def processFileList(filesList):
    files = []
    for file in filesList:
        files.append(FileObject.objects.get(id = file['id']))
    return files

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def RecruiterSubmitJAF(request,form_id=None):

    if request.user.role != 'recruiter':
        return Response({'error': 'Please login as recruiter'}, status=400)
    
    if not request.body:
        return Response({'error': 'Please provide JAF form Info'}, status=400)
    data = json.loads(request.body)
    save_as_draft = data.get('save_as_draft', None)
    form_data = data.get('form_data', None)
    versionTitle = data.get('versionTitle', None)
    submitted_by = User.objects.get(email=request.user.email)

    if JAFForm.objects.filter(versionTitle=versionTitle, submitted_by=submitted_by).exists():
        return Response({'error': 'JAF form with this version title already exists'}, status=400)



    if form_data:
        JAF_Form=None 
        if( form_id is None):
            JAF_Form = JAFForm.objects.create(
                submitted_by = submitted_by,
                organisation_name = form_data.get('organisation_name', None),
                organisation_postal_address = form_data.get('organisation_postal_address', None),
                organisation_website = form_data.get('organisation_website', None),
                versionTitle=versionTitle,
                organisation_type_options = form_data.get('organisation_type_options', None),
                organisation_type_others = form_data.get('organisation_type_others', None),
                industry_sector_options = form_data.get('industry_sector_options', None),
                industry_sector_others = form_data.get('industry_sector_others', None),
                job_profile_designation = form_data.get('job_profile_designation', None),
                job_profile_job_description = form_data.get('job_profile_job_description', None),
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
            JAF_Form.job_profile_job_description_pdf.add(*processFileList(form_data['job_profile_job_description_pdf']))
            JAF_Form.save()
            
            send_mails(request.user.email,User.objects.get(email=request.user.email).company_name,'JAF')

            return Response({'success': 'JAF form created successfully',"form_id":JAF_Form.id}, status=200)
        elif JAFForm.objects.filter(id=form_id).exists:
            JAF_Form=JAFForm.objects.get(id=form_id)
            JAF_Form.submitted_by = submitted_by
            JAF_Form.organisation_name = form_data.get('organisation_name', None)
            JAF_Form.organisation_postal_address = form_data.get('organisation_postal_address', None)
            JAF_Form.organisation_website = form_data.get('organisation_website', None)
            JAF_Form.versionTitle=versionTitle
            JAF_Form.organisation_type_options = form_data.get('organisation_type_options', None)
            JAF_Form.organisation_type_others = form_data.get('organisation_type_others', None)
            JAF_Form.industry_sector_options = form_data.get('industry_sector_options', None)
            JAF_Form.industry_sector_others = form_data.get('industry_sector_others', None)
            JAF_Form.job_profile_designation = form_data.get('job_profile_designation', None)
            JAF_Form.job_profile_job_description = form_data.get('job_profile_job_description', None)
            JAF_Form.job_profile_job_description_pdf.clear()
            JAF_Form.job_profile_job_description_pdf.add(*processFileList(form_data['job_profile_job_description_pdf']))
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
            send_mails()

            send_mails(request.user.email,User.objects.get(email=request.user.email).company_name,'JAF')

            return Response({'success': 'JAF form updated successfully'}, status=200)
        else:
            return Response({'error': 'Invalid form id'}, status=400) 
    else:
        return Response({'error': 'Please provide JAF form data'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def RecruiterINF(request,form_id=None):

    if request.user.role != 'recruiter':
        return Response({'error': 'Please login as recruiter'}, status=400)
    
    email = request.user.email
    if( User.objects.filter(email=email).exists() == False):
        return Response({'error': 'Recruiter is not present on portal'}, status=400)
    
    # if request contains a form id, then return that form
    if form_id is not None:
        INF_Form = INFForm.objects.filter(id=form_id).first()
        if not INF_Form:
            return Response({'error': 'Invalid form id'}, status=400)
        INF_data={
            'organisation_name': INF_Form.organisation_name,
            'organisation_postal_address': INF_Form.organisation_postal_address,
            'organisation_website': INF_Form.organisation_website,
            'versionTitle': INF_Form.versionTitle,
            'organisation_type_options': INF_Form.organisation_type_options,
            'organisation_type_others': INF_Form.organisation_type_others,
            'industry_sector_options': INF_Form.industry_sector_options,
            'industry_sector_others': INF_Form.industry_sector_others,
            'job_profile_designation': INF_Form.job_profile_designation,
            'job_profile_job_description': INF_Form.job_profile_job_description,
            'job_profile_job_description_pdf': fileObjectsToJson(INF_Form.job_profile_job_description_pdf.all()),
            'job_profile_place_of_posting': INF_Form.job_profile_place_of_posting,
            'contact_details_head_hr': ObjectToJSON_ContactDetails(INF_Form.contact_details_head_hr),
            'contact_details_first_person_of_contact': ObjectToJSON_ContactDetails(INF_Form.contact_details_first_person_of_contact),
            'contact_details_second_person_of_contact': ObjectToJSON_ContactDetails(INF_Form.contact_details_second_person_of_contact),
            'stipend_details_stipend_amount': INF_Form.stipend_details_stipend_amount,
            'stipend_details_bonus_perks_incentives': INF_Form.stipend_details_bonus_perks_incentives,
            'stipend_details_accodation_trip_fare': INF_Form.stipend_details_accodation_trip_fare,
            'stipend_details_bonus_service_contract': INF_Form.stipend_details_bonus_service_contract,
            'job_profile_two_months_intern': INF_Form.job_profile_two_months_intern,
            'job_profile_six_months_intern': INF_Form.job_profile_six_months_intern,
            'job_profile_joint_master_thesis_program': INF_Form.job_profile_joint_master_thesis_program,
            'selection_process': ObjectToJSON_SelectionProcess(INF_Form.selection_process)
        }
        return Response({'Data': INF_data}, status=200)
        
    user_email = User.objects.get(email=email)
    INF_FormList = INFForm.objects.filter(submitted_by=user_email).values('id', 'timestamp', 'is_draft','versionTitle')
    return Response({'INF_list': list(INF_FormList)}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def RecruiterSubmitINF(request,form_id=None):

    if request.user.role != 'recruiter':
        return Response({'error': 'Please login as recruiter'}, status=400)
    
    if not request.body:
        return Response({'error': 'Please provide INF form Info'}, status=400)
    data = json.loads(request.body)
    save_as_draft = data.get('save_as_draft', None)
    form_data = data.get('form_data', None)
    versionTitle = data.get('versionTitle', None)
    submitted_by = User.objects.get(email=request.user.email)

    if INFForm.objects.filter(versionTitle=versionTitle, submitted_by=submitted_by).exists():
        return Response({'error': 'INF form with this version title already exists'}, status=400)


        
    if form_data:
        INF_Form=None
        if( form_id is None):
            INF_Form = INFForm.objects.create(
                submitted_by=submitted_by,
                organisation_name=form_data.get('organisation_name', None),
                organisation_postal_address=form_data.get('organisation_postal_address', None),
                organisation_website=form_data.get('organisation_website', None),
                versionTitle=versionTitle,
                organisation_type_options=form_data.get('organisation_type_options', None),
                organisation_type_others=form_data.get('organisation_type_others', None),
                industry_sector_options=form_data.get('industry_sector_options', None),
                industry_sector_others=form_data.get('industry_sector_others', None),
                job_profile_designation=form_data.get('job_profile_designation', None),
                job_profile_job_description=form_data.get('job_profile_job_description', None),
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
            INF_Form.job_profile_job_description_pdf.add(*processFileList(form_data['job_profile_job_description_pdf']))
            INF_Form.save()

            send_mails(request.user.email,User.objects.get(email=request.user.email).company_name,'INF')

            return Response({'success': 'INF form created successfully',"form_id":INF_Form.id}, status=200)
        elif INFForm.objects.filter(id=form_id).exists:
            INF_Form=INFForm.objects.get(id=form_id)
            INF_Form.submitted_by=submitted_by
            INF_Form.organisation_name=form_data.get('organisation_name', None)
            INF_Form.organisation_postal_address=form_data.get('organisation_postal_address', None)
            INF_Form.organisation_website=form_data.get('organisation_website', None)
            INF_Form.versionTitle=versionTitle
            INF_Form.organisation_type_options=form_data.get('organisation_type_options', None)
            INF_Form.organisation_type_others=form_data.get('organisation_type_others', None)
            INF_Form.industry_sector_options=form_data.get('industry_sector_options', None)
            INF_Form.industry_sector_others=form_data.get('industry_sector_others', None)
            INF_Form.job_profile_designation=form_data.get('job_profile_designation', None)
            INF_Form.job_profile_job_description=form_data.get('job_profile_job_description', None)
            INF_Form.job_profile_job_description_pdf.clear()
            INF_Form.job_profile_job_description_pdf.add(*processFileList(form_data['job_profile_job_description_pdf']))
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

            send_mails(request.user.email,User.objects.get(email=request.user.email).company_name,'INF')

            return Response({'success': 'INF form updated successfully'}, status=200)
        else:
            return Response({'error': 'Invalid form id'}, status=400)            
    else:
        return Response({'error': 'Please provide INF form Data'}, status=400)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def SpocDetails(request):

    if request.user.role != 'recruiter':
        return Response({'error': 'Please login as recruiter'}, status=400)
    
    email = request.user.email

    spoc_info = SpocCompany.objects.filter(HREmail=email).first()
    
    if not spoc_info:
        return Response({'error': 'No Spoc is currently assigned'}, status=200)
    
    if( User.objects.filter(email=spoc_info.spocEmail).exists() == False):
        return Response({'error': 'Spoc is not present on portal'}, status=400)
    
    spoc_details = User.objects.get(email=spoc_info.spocEmail)
    return Response({'Name':spoc_details.name,'Phone': spoc_details.phone,"Email":spoc_details.email}, status=200)
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def DepartmentPrograms(request,degree):

    if not InterestedDiscipline.objects.filter(degree=degree).exists():
        return Response({'error': 'Invalid degree'}, status=400)
    
    branch = InterestedDiscipline.objects.filter(degree=degree).values('branch')

    return Response(branch[0], status=200)
        

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def JDFileUpload(request,form_id):

#     if request.user.role != 'recruiter':
#         return Response({'error': 'Please login as recruiter'}, status=400)

#     JAF_Form = JAFForm.objects.filter(id=form_id).first()

#     if not JAF_Form:
#         return Response({'error': 'Invalid form id'}, status=400)

#     if( request.FILES['file'].name != str(form_id)+'.pdf'):
#         return Response({'error': 'Invalid file name'}, status=400)
    
#     JAF_Form.job_profile_job_description_pdf = request.FILES['file']
#     JAF_Form.save()
#     return Response({'success': 'File uploaded successfully'}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def JDFileUpload(request):
    if request.user.role != 'recruiter':
        return Response({'error': 'Please login as recruiter'}, status=400)
    
    try:
        uploadedFileObject = FileObject.objects.create(file=request.FILES['file'],file_name=request.FILES['file'].name, uploaded_by=request.user)
        uploadedFileObject.save()
        response = {
            'id': uploadedFileObject.id,
            'file_name': uploadedFileObject.file_name,
        }
        return Response(response, status=200)
    except:
        return Response({'error': 'Unsupported format or file-size'}, status=400)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def JDFileDownload(request,form_id):

#     if request.user.role != 'recruiter':
#         return Response({'error': 'Please login as recruiter'}, status=400)

#     file_data=None
#     try:
#         file_data=open('media/job_description_pdfs/'+str(form_id)+'.pdf','rb').read()
#     except:
#         return Response({'error': 'File not found'}, status=400)
#     response=HttpResponse(file_data,content_type='application/pdf')    
#     return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def JDFileDownload(request, id):
    try:
        myFile = FileObject.objects.get(id=id)
        if(request.user.role != 'recruiter' or myFile.uploaded_by == request.user):
            response = HttpResponse(myFile.file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename='+myFile.file_name
        else:
            response = Response({'error': 'You are not authorised to download this file'}, status=400)
        return response
    except:
        return Response({'error': 'File not found'}, status=400)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def SpocJAF(request,form_id=None):

    if request.user.role.lower() != 'spoc':
        return Response({'error': 'Please login as Spoc'}, status=400)
    
    email=request.user.email

    HR_list = SpocCompany.objects.filter(spocEmail=email).values('HREmail')



    if not HR_list:
        return Response({'error': 'No company is currently assigned'}, status=400)

    # organisation_name_list = set()


    # for HR in HR_list:
    #     organisation_name_list.add(User.objects.get(email=HR['HREmail']).company_name)

    HR_list_id = set()

    for HR in HR_list:
        HR_list_id.add(User.objects.get(email=HR['HREmail']).id)

    HR_list_email = [User.objects.get(id=HR_id).email for HR_id in HR_list_id]
    HR_list = HR_list_id


    if form_id is not None:
        JAF_Form = JAFForm.objects.filter(id=form_id).first()
        if not JAF_Form:
            return Response({'error': 'Invalid form id'}, status=400)
        
        # if JAF_Form.organisation_name not in organisation_name_list:
        #     return Response({'error': 'Not spoc of respective company'}, status=400)

        if JAF_Form.submitted_by.email not in HR_list_email:
            return Response({'error': 'Not spoc of respective company'}, status=400)

        JAF_data = {
            'organisation_name': JAF_Form.organisation_name,
            'organisation_postal_address': JAF_Form.organisation_postal_address,
            'organisation_website': JAF_Form.organisation_website,
            'versionTitle': JAF_Form.versionTitle,
            'organisation_type_options': JAF_Form.organisation_type_options,
            'organisation_type_others': JAF_Form.organisation_type_others,
            'industry_sector_options': JAF_Form.industry_sector_options,
            'industry_sector_others': JAF_Form.industry_sector_others,
            'job_profile_designation': JAF_Form.job_profile_designation,
            'job_profile_job_description': JAF_Form.job_profile_job_description,
            'job_profile_job_description_pdf': fileObjectsToJson(JAF_Form.job_profile_job_description_pdf.all()),
            'job_profile_place_of_posting': JAF_Form.job_profile_place_of_posting,
            'contact_details_head_hr': ObjectToJSON_ContactDetails(JAF_Form.contact_details_head_hr),
            'contact_details_first_person_of_contact': ObjectToJSON_ContactDetails(JAF_Form.contact_details_first_person_of_contact),
            'contact_details_second_person_of_contact': ObjectToJSON_ContactDetails(JAF_Form.contact_details_second_person_of_contact),
            'salary_details_b_tech': ObjectToJSON_SalaryDetails(JAF_Form.salary_details_b_tech),
            'salary_details_m_tech': ObjectToJSON_SalaryDetails(JAF_Form.salary_details_m_tech),
            'salary_details_m_sc': ObjectToJSON_SalaryDetails(JAF_Form.salary_details_m_sc),
            'salary_details_phd': ObjectToJSON_SalaryDetails(JAF_Form.salary_details_phd),
            'selection_process': ObjectToJSON_SelectionProcess(JAF_Form.selection_process)
        } 
        return Response( {"Data": JAF_data}, status=200)
    
    # JAF_FormList = JAFForm.objects.filter(organisation_name__in=organisation_name_list).values('id', 'timestamp', 'is_draft','versionTitle','submitted_by')
    JAF_FormList = JAFForm.objects.filter(submitted_by__in=HR_list).values('id', 'timestamp', 'is_draft','versionTitle','submitted_by')

    return Response({'JAF_list': list(JAF_FormList)}, status=200)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def SpocINF(request,form_id=None):
    if request.user.role.lower() != 'spoc':
        return Response({'error': 'Please login as Spoc'}, status=400)
    
    email=request.user.email

    HR_list = SpocCompany.objects.filter(spocEmail=email).values('HREmail')



    if not HR_list:
        return Response({'error': 'No company is currently assigned'}, status=400)

    # organisation_name_list = set()


    # for HR in HR_list:
    #     organisation_name_list.add(User.objects.get(email=HR['HREmail']).company_name)

    HR_list_id = set()

    for HR in HR_list:
        HR_list_id.add(User.objects.get(email=HR['HREmail']).id)

    HR_list_email = [User.objects.get(id=HR_id).email for HR_id in HR_list_id]
    HR_list = HR_list_id


    if form_id is not None:
        INF_Form = INFForm.objects.filter(id=form_id).first()
        if not INF_Form:
            return Response({'error': 'Invalid form id'}, status=400)
        
        # if INF_Form.organisation_name not in organisation_name_list:
        #     return Response({'error': 'Not spoc of respective company'}, status=400)

        if INF_Form.submitted_by.email not in HR_list_email:
            return Response({'error': 'Not spoc of respective company'}, status=400)


        INF_data={
            'organisation_name': INF_Form.organisation_name,
            'organisation_postal_address': INF_Form.organisation_postal_address,
            'organisation_website': INF_Form.organisation_website,
            'versionTitle': INF_Form.versionTitle,
            'organisation_type_options': INF_Form.organisation_type_options,
            'organisation_type_others': INF_Form.organisation_type_others,
            'industry_sector_options': INF_Form.industry_sector_options,
            'industry_sector_others': INF_Form.industry_sector_others,
            'job_profile_designation': INF_Form.job_profile_designation,
            'job_profile_job_description': INF_Form.job_profile_job_description,
            'job_profile_job_description_pdf': fileObjectsToJson(INF_Form.job_profile_job_description_pdf.all()),
            'job_profile_place_of_posting': INF_Form.job_profile_place_of_posting,
            'contact_details_head_hr': ObjectToJSON_ContactDetails(INF_Form.contact_details_head_hr),
            'contact_details_first_person_of_contact': ObjectToJSON_ContactDetails(INF_Form.contact_details_first_person_of_contact),
            'contact_details_second_person_of_contact': ObjectToJSON_ContactDetails(INF_Form.contact_details_second_person_of_contact),
            'stipend_details_stipend_amount': INF_Form.stipend_details_stipend_amount,
            'stipend_details_bonus_perks_incentives': INF_Form.stipend_details_bonus_perks_incentives,
            'stipend_details_accodation_trip_fare': INF_Form.stipend_details_accodation_trip_fare,
            'stipend_details_bonus_service_contract': INF_Form.stipend_details_bonus_service_contract,
            'job_profile_two_months_intern': INF_Form.job_profile_two_months_intern,
            'job_profile_six_months_intern': INF_Form.job_profile_six_months_intern,
            'job_profile_joint_master_thesis_program': INF_Form.job_profile_joint_master_thesis_program,
            'selection_process': ObjectToJSON_SelectionProcess(INF_Form.selection_process)
        }
        return Response({'Data': INF_data}, status=200)
    
    # INF_FormList = INFForm.objects.filter(organisation_name__in=organisation_name_list).values('id', 'timestamp', 'is_draft','versionTitle','submitted_by')
    
    INF_FormList = INFForm.objects.filter(submitted_by__in=HR_list).values('id', 'timestamp', 'is_draft','versionTitle','submitted_by')

    return Response({'INF_list': list(INF_FormList)}, status=200)

@api_view(['GET'])
def GetBranches(request):
    output = {
        'BTech': [],
        'BTech with minor in': [],
        'Dual Degree': [],
        'MTech': [],
        'MSc': [],
        'PhD': []
    }
    for branch in Branch.objects.all():
        output[branch.degree].append(branch.shortcut)
    return Response(output, status=200)
