from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, UserUser


admin.site.register(Follow)


class UserAdmin(UserAdmin):
    ordering = ["id"]
    list_filter = ("username", "email")
    list_display = ["email", "username"]
    fieldsets = (
        (("Information"),
            {"fields":
                ("first_name", "email", "username", "password")
             }
         ),
        (("Important dates"), {"fields": ("last_login",)}),
    )


admin.site.register(UserUser, UserAdmin)
