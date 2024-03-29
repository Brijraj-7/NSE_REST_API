from django.contrib import admin
from .models import IndexPrice, Index
from import_export.admin import ImportExportModelAdmin

@admin.register(IndexPrice)
class IndexPriceAdmin(ImportExportModelAdmin):
    list_display = ('index','index_id','date', 'open', 'high', 'low', 'close', 'sharestraded', 'turnover')

@admin.register(Index)
class IndexAdmin(ImportExportModelAdmin):
    list_display = ('id','name',)
    index_id = id
