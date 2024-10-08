from django.contrib import admin
from django.http import HttpResponseRedirect
from .models import Video
from django.utils.html import format_html
from django.urls import path
from django.utils.translation import gettext_lazy as _


class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'genre', 'rq_dashboard_link')
    readonly_fields = ('id',)

    def rq_dashboard_link(self, obj):
        return format_html('<a href="{}" target="_blank">RQ Dashboard</a>', '/django-rq/')

    rq_dashboard_link.short_description = 'RQ Dashboard'



class RQDashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/rq_dashboard_link.html"

    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect('/django-rq/')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('rq-dashboard/', self.admin_site.admin_view(self.changelist_view), name="rq_dashboard"),
        ]
        return custom_urls + urls


admin.site.register(Video, VideoAdmin)
admin.site.site_header = _('Streamada Admin-Panel')
admin.site.site_title = _('Streamada Server')
admin.site.index_title = _('Streamada administration')

