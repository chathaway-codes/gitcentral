from django.contrib import admin

from .models import *

admin.site.register(Key)
admin.site.register(Repo)
admin.site.register(RepoPermission)
