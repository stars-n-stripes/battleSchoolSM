from django.contrib import admin

# Register your models here.
from .models import Flag, VM, Scenario, Student

admin.site.register(Flag)
admin.site.register(VM)
admin.site.register(Scenario)
admin.site.register(Student)