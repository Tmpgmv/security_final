from django.contrib import admin
from django.contrib.auth.admin import UserAdmin



# PREP {
from .models import User

admin.site.register(User, UserAdmin)

# } PREP

