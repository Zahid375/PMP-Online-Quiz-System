from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Quiz)
admin.site.register(Topic)
admin.site.register(Choice)
admin.site.register(Result)


class ChoiceInLineAdmin(admin.TabularInline):
    model = Choice


class AuthorAdmin(admin.ModelAdmin):
    inlines = [ChoiceInLineAdmin]


admin.site.register(Question, AuthorAdmin)
