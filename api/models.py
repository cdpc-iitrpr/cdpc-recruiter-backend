from typing_extensions import override
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
# Create your models here.

class User(AbstractUser):
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

class ContactDetails(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)

class SalaryDetails(models.Model):
    ctc_gross = models.TextField()
    ctc_take_home = models.TextField()
    ctc_bonus_perks = models.TextField()
    bond_contract = models.TextField()

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
    interested_discipline = ArrayField(models.JSONField(default=dict, blank=True))


class Form(models.Model):
    organisation_name = models.CharField(max_length=255)
    organisation_postal_address = models.TextField()
    organisation_website = models.URLField()
    
    organisation_type_options = ArrayField(models.TextField())
    organisation_type_others = models.TextField()

    industry_sector_options = ArrayField(models.TextField(),default=list)
    industry_sector_others = models.TextField()
    
    job_profile_designation = models.CharField(max_length=255)
    job_profile_job_description = models.TextField()
    job_profile_job_description_pdf = ArrayField(models.FileField(upload_to='job_description_pdfs/'))
    job_profile_place_of_posting = models.CharField(max_length=255)
    
    class Meta:
        abstract = True

class JAFForm(Form):
    pass
    contact_details_head_hr = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='head_hrJAF')
    contact_details_first_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='first_person_of_contactJAF')
    contact_details_second_person_of_contact = models.ForeignKey(ContactDetails, on_delete=models.CASCADE, related_name='second_person_of_contactJAF')
    salary_details_b_tech = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='b_tech')
    salary_details_m_tech = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='m_tech')
    salary_details_m_sc = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='m_sc')
    salary_details_phd = models.ForeignKey(SalaryDetails, on_delete=models.CASCADE, related_name='phd')
    selection_process = models.ForeignKey(SelectionProcess, on_delete=models.CASCADE, related_name='selection_processJAF')


class INFForm(Form):
    pass
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