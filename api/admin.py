from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


class MyAdmin(UserAdmin):
    list_display = ('username','email','is_staff','last_login')
    search_fields = ('username','email')
    readonly_fields = ('last_login','date_joined', 'id',)
    filter_horizontal = ()
    add_fieldsets = (
            (
                None,
                {
                    'classes': ('wide',),
                    'fields': ('username', 'email', 'password1', 'password2'),
                },
            ),
        )
    list_filter= ()
    fieldsets = ()

# Register your models here.
admin.site.register(User,MyAdmin)
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
