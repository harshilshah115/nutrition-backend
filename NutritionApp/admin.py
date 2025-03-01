from django.contrib import admin
from .models import *
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name","gender","email","goal")
admin.site.register(Profile, ProfileAdmin)

class MealAdmin(admin.ModelAdmin):
    list_display = ("title","calories")
admin.site.register(Meal, MealAdmin)
