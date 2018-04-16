from django.contrib import admin
from django.contrib.auth.models import Group
from . import models


class PyOTPAdmin(admin.ModelAdmin):
    """

    """
    list_display = ('id', 'uuid', 'secret', 'created_at',)
    list_display_links = ('uuid',)
    search_fields = ('uuid', 'secret',)
    list_per_page = 20
    ordering = ('-id',)

admin.site.register(models.PyOTP, PyOTPAdmin)
admin.site.unregister(Group)
