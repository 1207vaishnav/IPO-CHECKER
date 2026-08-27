from django.contrib import admin
from .models import IPO, PAN, Allotment


admin.site.register(PAN)
admin.site.register(IPO)
admin.site.register(Allotment)