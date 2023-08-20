from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from random import randint
# Create your models here.

class User(AbstractUser):
    name= models.CharField(max_length=255,null=False,blank=False)
    email = models.EmailField(unique=True,null=False,blank=False)
    phone = models.CharField(max_length=15, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='api_users',  # Unique related_name for the groups field
        blank=True,
        verbose_name=_('groups'),
        help_text=_('The groups this user belongs to.'),
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='api_users',  # Unique related_name for the user_permissions field
        blank=True,
        verbose_name=_('user permissions'),
        help_text=_('Specific permissions for this user.'),
    )

    def __str__(self):
        return self.email

class UserOTP(models.Model):
    email = models.EmailField(unique=True,null=False,blank=False)
    secret_key = models.CharField(max_length=255,null=False,blank=False)
    created_at = models.DateTimeField(auto_now=True)

class SpocCompany(models.Model):
    spocEmail=models.EmailField(null=False,blank=False)
    HREmail=models.EmailField()

    def __str__(self):
        return self.spocEmail+"("+self.HREmail+")"

class ContactDetails(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    mobile = models.TextField(null=True,blank=True)
    phone = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name+"("+self.email+")"

class SalaryDetails(models.Model):
    ctc_gross = models.TextField(null=True)
    ctc_take_home = models.TextField(null=True)
    ctc_bonus_perks = models.TextField(null=True)
    bond_contract = models.TextField(null=True)

class TestType(models.Model):
    ppt = models.BooleanField(null=True)
    shortlist_from_resume = models.BooleanField(null=True)
    written_test = models.BooleanField(null=True)
    online_test = models.BooleanField(null=True)
    technical_test = models.BooleanField(null=True)
    aptitude_test = models.BooleanField(null=True)
    psychometric_test = models.BooleanField(null=True)
    group_discussion = models.BooleanField(null=True)
    personal_interview = models.BooleanField(null=True)

class InterestedDiscipline(models.Model):
    
    degree = models.CharField(max_length=50,null=False,blank=False,primary_key=True)
    branch = ArrayField(models.TextField())

    def __str__(self):
        return self.degree

class SelectionProcess(models.Model):
    eligibility_criteria = models.TextField(null=True,blank=True)
    allow_backlog_students = models.BooleanField(null=True,blank=True)
    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE,null=True,blank=True)
    test_duration = models.CharField(max_length=50,null=True,blank=True)
    likely_topics = models.TextField(null=True,blank=True)
    number_of_rounds = models.PositiveIntegerField(null=True,blank=True)
    group_discussion_duration = models.CharField(max_length=50,null=True,blank=True)
    number_of_offers = models.PositiveIntegerField(null=True,blank=True)
    preferred_period = models.CharField(max_length=50,null=True,blank=True)
    logistics_requirements = models.TextField(null=True,blank=True)
    interested_discipline = models.JSONField(null=True,blank=True)

def fileSavePath(instance, filename):
    random_number = randint(1000000000, 9999999999)
    return 'jaf_pdfs/{0}/{1}_{2}'.format(instance.id, random_number, filename)
class FileObject(models.Model):
    file = models.FileField(upload_to=fileSavePath, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class Form(models.Model):
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
    organisation_name = models.CharField(max_length=255,null=True,blank=True)
    organisation_postal_address = models.TextField(null=True,blank=True)
    organisation_website = models.URLField(null=True,blank=True)
    versionTitle = models.CharField(max_length=255,null=True,blank=True)

    organisation_type_options = ArrayField(models.TextField(),null=True,blank=True)
    organisation_type_others = models.TextField(null=True,blank=True)

    industry_sector_options = ArrayField(models.TextField(),null=True,blank=True)
    industry_sector_others = models.TextField(null=True,blank=True)
    
    job_profile_designation = models.CharField(max_length=255,null=True,blank=True)
    job_profile_job_description = models.TextField(null=True,blank=True)
    job_profile_job_description_pdf = models.ManyToManyField(FileObject,  blank=True, null=True)
    job_profile_place_of_posting = models.CharField(max_length=255,null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True,blank=True)
    is_draft = models.BooleanField(null=False,blank=False)
    class Meta:
        abstract = True

class JAFForm(Form):
    contact_details_head_hr = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='head_hrJAF', null=True, blank=True)
    contact_details_first_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='first_person_of_contactJAF',null=True, blank=True)
    contact_details_second_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='second_person_of_contactJAF',null=True, blank=True)
    salary_details_b_tech = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='b_tech',null=True, blank=True)
    salary_details_m_tech = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='m_tech',null=True, blank=True)
    salary_details_m_sc = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='m_sc',null=True, blank=True)
    salary_details_phd = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='phd',null=True, blank=True)
    selection_process = models.ForeignKey(SelectionProcess, on_delete=models.CASCADE, related_name='selection_processJAF',null=True, blank=True)

class INFForm(Form):
    contact_details_head_hr = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='head_hrINF',null=True, blank=True)
    contact_details_first_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='first_person_of_contactINF',null=True, blank=True)
    contact_details_second_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='second_person_of_contactINF',null=True, blank=True)
    job_profile_two_months_intern = models.BooleanField(null=True,blank=True)
    job_profile_six_months_intern = models.BooleanField(null=True,blank=True)
    job_profile_joint_master_thesis_program = models.BooleanField(null=True,blank=True)

    stipend_details_stipend_amount = models.TextField(null=True,blank=True)
    stipend_details_bonus_perks_incentives = models.TextField(null=True,blank=True)
    stipend_details_accodation_trip_fare = models.TextField(null=True,blank=True)
    stipend_details_bonus_service_contract = models.TextField(null=True,blank=True)
    selection_process = models.ForeignKey(SelectionProcess, on_delete=models.CASCADE, related_name='selection_processINF',null=True, blank=True)

class Branch(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False,primary_key=True)
    shortcut = models.CharField(max_length=10,null=False,blank=False)
    # degree choices

    class Degree(models.TextChoices):
        BTECH = 'BTech', _('BTech')
        BTECHMINOR = 'BTech with minor in', _('BTech with minor in')
        DUALDEGREE = 'Dual Degree', _('Dual Degree')
        MTECH = 'MTech', _('MTech')
        MSC = 'MSc', _('MSc')
        PHD = 'PhD', _('PhD')

    degree = models.CharField(choices=Degree.choices, max_length= 30)

    def __str__(self):
        return self.name