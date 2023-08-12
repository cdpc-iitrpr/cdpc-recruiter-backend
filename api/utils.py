from .models import *

def AddContactDetails(contactInfo):
    if(contactInfo==None):
        return None
    if( contactInfo.get('email')==None or contactInfo.get('email')==None or contactInfo.get('phone')==None):
        return None

    contact_details = ContactDetails.objects.create(
        name =  contactInfo['name'],
        email = contactInfo['email'],
        mobile = contactInfo['mobile'] if 'mobile' in contactInfo else None,
        phone = contactInfo['phone']
    )
    return contact_details

def AddSalaryDetails(salaryInfo):

    if(salaryInfo==None):
        return None

    salary_details = SalaryDetails.objects.create(
        ctc_gross = salaryInfo['ctc_gross'] if 'ctc_gross' in salaryInfo else None,
        ctc_take_home = salaryInfo['ctc_take_home'] if 'ctc_take_home' in salaryInfo else None,
        ctc_bonus_perks = salaryInfo['ctc_bonus_perks'] if 'ctc_bonus_perks' in salaryInfo else None,
        bond_contract = salaryInfo['bond_contract'] if 'bond_contract' in salaryInfo else None
    )
    return salary_details

def AddSelectionProcess(selectionProcessInfo):

    if(selectionProcessInfo==None):
        return None

    # print("###")
    # # print(selectionProcessInfo['interested_discipline']) 
    # a=InterestedDiscipline.objects.filter(degree= selectionProcessInfo['interested_discipline'])    
    # print(a[0])
    # print("###")

    selection_process = SelectionProcess.objects.create(
        eligibility_criteria = selectionProcessInfo['eligibility_criteria'] if 'eligibility_criteria' in selectionProcessInfo else None,
        allow_backlog_students = selectionProcessInfo['allow_backlog_students'] if 'allow_backlog_students' in selectionProcessInfo else False,
        test_duration = selectionProcessInfo['test_duration'] if 'test_duration' in selectionProcessInfo else None,
        likely_topics = selectionProcessInfo['likely_topics'] if 'likely_topics' in selectionProcessInfo else None,
        number_of_rounds = selectionProcessInfo['number_of_rounds'] if 'number_of_rounds' in selectionProcessInfo else None,
        group_discussion_duration = selectionProcessInfo['group_discussion_duration'] if 'group_discussion_duration' in selectionProcessInfo else None,
        number_of_offers  = selectionProcessInfo['number_of_offers'] if 'number_of_offers' in selectionProcessInfo else None,
        preferred_period = selectionProcessInfo['preferred_period'] if 'preferred_period' in selectionProcessInfo else None,
        logistics_requirements = selectionProcessInfo['logistics_requirements'] if 'logistics_requirements' in selectionProcessInfo else None,
        interested_discipline = InterestedDiscipline.objects.get(degree= selectionProcessInfo['interested_discipline']) if 'interested_discipline' in selectionProcessInfo else None,
        test_type = AddTestType(selectionProcessInfo['test_type']) 

    )
    return selection_process

def AddTestType(testTypeInfo):

    if(testTypeInfo==None):
        return None

    test_type = TestType.objects.create(
        ppt = testTypeInfo['ppt'] if 'ppt' in testTypeInfo else False,
        shortlist_from_resume = testTypeInfo['shortlist_from_resume'] if 'shortlist_from_resume' in testTypeInfo else False,
        written_test = testTypeInfo['written_test'] if 'written_test' in testTypeInfo else False,
        online_test = testTypeInfo['online_test'] if 'online_test' in testTypeInfo else False,
        technical_test = testTypeInfo['technical_test'] if 'technical_test' in testTypeInfo else False,
        aptitude_test = testTypeInfo['aptitude_test'] if 'aptitude_test' in testTypeInfo else False,
        psychometric_test = testTypeInfo['psychometric_test'] if 'psychometric_test' in testTypeInfo else False,
        group_discussion = testTypeInfo['group_discussion'] if 'group_discussion' in testTypeInfo else False,
        personal_interview = testTypeInfo['personal_interview'] if 'personal_interview' in testTypeInfo else False,

    )
    return test_type
