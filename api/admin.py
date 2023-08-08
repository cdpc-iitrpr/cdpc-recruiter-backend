from django.contrib import admin
from .models import User,JAFForm,INFForm,ContactDetails,SalaryDetails,TestType,SelectionProcess
# Register your models here.
admin.site.register(User,admin.ModelAdmin)
admin.site.register(JAFForm,admin.ModelAdmin)
admin.site.register(INFForm,admin.ModelAdmin)
admin.site.register(TestType,admin.ModelAdmin)
admin.site.register(ContactDetails,admin.ModelAdmin)
admin.site.register(SalaryDetails,admin.ModelAdmin)
admin.site.register(SelectionProcess,admin.ModelAdmin)
