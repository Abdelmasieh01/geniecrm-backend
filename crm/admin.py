from django.contrib import admin
from .models import Lead, Stage

class LeadAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email"]

class StageAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]

admin.site.register(Lead, LeadAdmin)
admin.site.register(Stage, StageAdmin)