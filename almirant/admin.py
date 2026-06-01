
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count
from django.core.exceptions import PermissionDenied
from .models import ServerNode, LogEntry

class CustomAdminSite(admin.AdminSite):
    site_header = "Akainu Dashboard"
    site_title = "Akainu Admin"
    index_title = "Panel de Telemetría"

    def get_urls(self):
        custom_urls = [
            # MODIFICACIÓN 1: El decorador admin_view maneja la seguridad y caché automáticamente
            path('dashboard/', self.admin_view(self.dashboard_view), name='custom_dashboard')
        ]
        return custom_urls + super().get_urls()

    def dashboard_view(self, request):
        # NOTA: El filtro 'if not request.user.is_staff' ya lo maneja self.admin_view automáticamente
        
        # 1. Consultas básicas de conteo
        servers = ServerNode.objects.count()
        
        # MODIFICACIÓN 2: Optimización de conteo de anomalías usando .exists() o filtros específicos si aplica.
        anomalies = LogEntry.objects.filter(is_anomaly=True).count()
        
        # 2. Consulta para la gráfica
        logs_by_level = LogEntry.objects.values('level').annotate(total=Count('id'))
        
        # 3. Formatear los datos para Chart.js
        labels = [item['level'] for item in logs_by_level]
        data = [item['total'] for item in logs_by_level]

        context = dict(
            self.each_context(request),
            servers=servers,
            anomalies=anomalies,
            chart_labels=labels,
            chart_data=data,
            title="Dashboard Gráfico de Telemetría"
        )
        return TemplateResponse(request, "admin/dashboard.html", context)

# Instanciamos el sitio personalizado
admin_site = CustomAdminSite(name='custom_admin')

# MODIFICACIÓN 3: Registro limpio de modelos usando ModelAdmin dedicados
@admin.register(ServerNode, site=admin_site)
class ServerNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'environment', 'is_active')
    list_filter = ('environment', 'is_active')
    search_fields = ('name', 'ip_address')

@admin.register(LogEntry, site=admin_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'node', 'level', 'service_name', 'short_message', 'is_anomaly')
    list_filter = ('level', 'is_anomaly', 'node')
    search_fields = ('service_name', 'request_ip', 'message')
    # Optimización clave: Evita el problema N+1 queries haciendo un JOIN en la base de datos
    list_select_related = ('node',)
    # Hacer los logs de so
    # lo lectura en el admin para evitar alteraciones manuales de auditoría
    readonly_fields = ('timestamp', 'node', 'level', 'service_name', 'message', 'request_ip', 'anomaly_score', 'ai_metadata')