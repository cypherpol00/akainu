
from django.contrib import admin
from django.urls import path
from almirant.admin import admin_site
from almirant.views import ingest_logs

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/v1/telemetry/ingest/', ingest_logs, name='ingest_logs'),
]
