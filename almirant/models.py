from django.db import models

class ServerNode(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    environment = models.CharField(
        max_length=20, 
        choices=[('PROD', 'Producción'), ('STAGE', 'Staging'), ('DEV', 'Desarrollo')],
        default='DEV'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.environment})"


class LogEntry(models.Model):
    LEVEL_CHOICES = [
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Crítico'),
    ]

    node = models.ForeignKey(ServerNode, on_delete=models.CASCADE, related_name='logs')
    # MODIFICACIÓN 1: Cambiado auto_now_add=True por un valor por defecto o manual para telemetría histórica
    timestamp = models.DateTimeField(db_index=True) 
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, db_index=True)
    service_name = models.CharField(max_length=100, db_index=True) 
    message = models.TextField()
    request_ip = models.GenericIPAddressField(blank=True, null=True, db_index=True)
    
    # --- SECCIÓN DE INTELIGENCIA ARTIFICIAL ---
    is_anomaly = models.BooleanField(default=False, db_index=True)
    anomaly_score = models.FloatField(default=0.0, db_index=True) 
    ai_metadata = models.JSONField(blank=True, null=True) 

    # MODIFICACIÓN 2: La clase Meta y las propiedades DEBEN ir indentadas DENTRO del modelo
    class Meta:
        verbose_name_plural = "Log Entries"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'level']),
            models.Index(fields=['timestamp', 'is_anomaly']),
        ]

    # MODIFICACIÓN 3: El decorador property va dentro del modelo para que funcione con las instancias
    @property
    def short_message(self):
        """Muestra una vista previa limpia en el listado del Admin"""
        return self.message[:75] + '...' if len(self.message) > 75 else self.message