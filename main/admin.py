from django.contrib import admin
from main.models import *


class VacancyImageInline(admin.TabularInline):
    model = VacancyImage
    max_num = 1

@admin.register(Vacancy)
class JobAdmin(admin.ModelAdmin):
    inlines = [VacancyImageInline, ]


admin.site.register(Comment)
admin.site.register(Rating)
# admin.site.register(RatingStar)
admin.site.register(Like)



