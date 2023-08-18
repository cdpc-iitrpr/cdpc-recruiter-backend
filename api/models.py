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

class SpocCompany(models.Model):
    spocEmail=models.EmailField(null=False,blank=False)
    HREmail=models.EmailField()

    def __str__(self):
        return self.spocEmail+"("+self.HREmail+")"

class ContactDetails(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False)
    email = models.EmailField(null=False,blank=False)
    mobile = models.TextField(null=True,blank=True)
    phone = models.TextField(null=False,blank=False)

    def __str__(self):
        return self.name+"("+self.email+")"

class SalaryDetails(models.Model):
    ctc_gross = models.TextField(null=True)
    ctc_take_home = models.TextField(null=True)
    ctc_bonus_perks = models.TextField(null=True)
    bond_contract = models.TextField(null=True)

class TestType(models.Model):
    ppt = models.BooleanField()
    shortlist_from_resume = models.BooleanField()
    written_test = models.BooleanField()
    online_test = models.BooleanField()
    technical_test = models.BooleanField()
    aptitude_test = models.BooleanField()
    psychometric_test = models.BooleanField()
    group_discussion = models.BooleanField()
    personal_interview = models.BooleanField()

class InterestedDiscipline(models.Model):
    
    degree = models.CharField(max_length=50,null=False,blank=False,primary_key=True)
    branch = ArrayField(models.TextField())

    def __str__(self):
        return self.degree

class SelectionProcess(models.Model):
    eligibility_criteria = models.TextField()
    allow_backlog_students = models.BooleanField()
    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE)
    test_duration = models.CharField(max_length=50)
    likely_topics = models.TextField()
    number_of_rounds = models.PositiveIntegerField()
    group_discussion_duration = models.CharField(max_length=50)
    number_of_offers = models.PositiveIntegerField()
    preferred_period = models.CharField(max_length=50)
    logistics_requirements = models.TextField()
    interested_discipline = models.JSONField()

def fileSavePath(instance, filename):
    random_number = randint(1000000000, 9999999999)
    return 'jaf_pdfs/{0}/{1}_{2}'.format(instance.id, random_number, filename)
class FileObject(models.Model):
    file = models.FileField(upload_to=fileSavePath, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class Form(models.Model):
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    organisation_name = models.CharField(max_length=255,null=True)
    organisation_postal_address = models.TextField(null=True)
    organisation_website = models.URLField(null=True)
    versionTitle = models.CharField(max_length=255,null=True)

    organisation_type_options = ArrayField(models.TextField(),null=True)
    organisation_type_others = models.TextField(null=True)

    industry_sector_options = ArrayField(models.TextField(),null=True)
    industry_sector_others = models.TextField(null=True)
    
    job_profile_designation = models.CharField(max_length=255,null=True)
    job_profile_job_description = models.TextField(null=True)
    job_profile_job_description_pdf = models.ManyToManyField(FileObject,  blank=True, null=True)
    job_profile_place_of_posting = models.CharField(max_length=255,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField()
    class Meta:
        abstract = True

class JAFForm(Form):
    contact_details_head_hr = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='head_hrJAF')
    contact_details_first_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='first_person_of_contactJAF')
    contact_details_second_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='second_person_of_contactJAF')
    salary_details_b_tech = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='b_tech')
    salary_details_m_tech = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='m_tech')
    salary_details_m_sc = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='m_sc')
    salary_details_phd = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='phd')
    selection_process = models.ForeignKey(SelectionProcess, on_delete=models.CASCADE, related_name='selection_processJAF')

class INFForm(Form):
    contact_details_head_hr = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='head_hrINF')
    contact_details_first_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='first_person_of_contactINF')
    contact_details_second_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='second_person_of_contactINF')
    job_profile_two_months_intern = models.BooleanField()
    job_profile_six_months_intern = models.BooleanField()
    job_profile_joint_master_thesis_program = models.BooleanField()

    stipend_details_stipend_amount = models.TextField()
    stipend_details_bonus_perks_incentives = models.TextField()
    stipend_details_accodation_trip_fare = models.TextField()
    stipend_details_bonus_service_contract = models.TextField()
    selection_process = models.ForeignKey(SelectionProcess, on_delete=models.CASCADE, related_name='selection_processINF')

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