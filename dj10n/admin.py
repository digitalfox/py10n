# -*- coding: UTF-8 -*-

# Sébastien Renard (sebastien.renard@digitalfox.org)
# Code licensed under GNU GPL V2

from django.contrib import admin
from py10n.dj10n.models import Branch, Module, Translator, Pofile

class PofileAdmin(admin.ModelAdmin):
    list_display = ("name", "module", "translator", "startdate", "type")
    ordering = ("module","name")
    list_filter = ["type",]
    date_hierarchy = "startdate"
    search_fields = ["name", "module__name",
                     "translator__firstname", "translator__lastname", "translator__email"]

class ModuleAdmin(admin.ModelAdmin):
    list_display= ("name", "branch", "type", "urgent")
    ordering = ("branch", "name")
    list_filter = ["type"]
    search_fields = ["name",]

class ModuleAdminInline(admin.TabularInline):
    model=Module

class TranslatorAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "email")
    ordering = ("lastname",)
    search_fields = ["firstname", "lastname", "email"]

class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "path")
    ordering = ("name",)
    search_fields = ["name", "path"]
    inlines = [ModuleAdminInline,]


admin.site.register(Branch, BranchAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Translator, TranslatorAdmin)
admin.site.register(Pofile, PofileAdmin)