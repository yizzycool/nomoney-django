from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Case)
admin.site.register(Application)
admin.site.register(Hashtag)
admin.site.register(MiddleAgent)