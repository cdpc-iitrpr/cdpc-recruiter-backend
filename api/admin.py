from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User,admin.ModelAdmin)
admin.site.register(JAFForm,admin.ModelAdmin)
admin.site.register(INFForm,admin.ModelAdmin)
admin.site.register(TestType,admin.ModelAdmin)
admin.site.register(ContactDetails,admin.ModelAdmin)
admin.site.register(SalaryDetails,admin.ModelAdmin)
admin.site.register(SelectionProcess,admin.ModelAdmin)
admin.site.register(InterestedDiscipline,admin.ModelAdmin)
admin.site.register(SpocCompany,admin.ModelAdmin)
admin.site.register(FileObject,admin.ModelAdmin)
admin.site.register(UserOTP,admin.ModelAdmin)
# admin.site.register(Branch,admin.ModelAdmin)
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'degree')
    list_filter = ('degree',)
    search_fields = ('name',)
