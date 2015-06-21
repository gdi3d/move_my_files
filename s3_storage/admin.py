from django.contrib import admin
from s3_storage.models import S3ConnectionSettings
# Register your models here.
admin.site.register(S3ConnectionSettings)