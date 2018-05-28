from django.contrib import admin

from proteus.models import User, Processing, Contact, Align


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']


@admin.register(Processing)
class ProcessingAdmin(admin.ModelAdmin):
    list_display =  [
        'id_user', 'status', 'pdbid', 'cutoff', 'url', 'notification_user']
    readonly_fields = []
    list_filter = ['status']
    search_fields = ['pdbid']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'id_p', 'ctt_type', 'ctt_sequence', 'ctt_status',
        'ctt_clash', 'ctt_ddg']
    readonly_fields = ['ctt_ddg', 'ctt_clash']


@admin.register(Align)
class AlignAdmin(admin.ModelAdmin):
    list_display = ['id_ctt', 'al_type', 'al_score', 'r1', 'r2', 'clash', 'ddg']