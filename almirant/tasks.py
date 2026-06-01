from celery import shared_task
from django.utils.dateparse import parse_datetime
from django.db import transaction
from .models import ServerNode, LogEntry
from .ai_detector import LogAnomalyDetector
import logging

logger = logging.getLogger(__name__)
detector = LogAnomalyDetector()

@shared_task(bind=True, name="akainu.tasks.process_logs_task", max_retries=3)
def process_logs_task(self, node_id, valid_logs, ignored_logs):
    """
    Worker en segundo plano: Ejecuta la IA de forma vectorial,
    reconstruye los datetimes y guarda masivamente.
    """
    try:
        node = ServerNode.objects.get(id=node_id)

        # 1. Evaluación con IA
        try:
            logs_analizados = detector.batch_predict(valid_logs)
        except Exception as ai_error:
            logger.error(f"Error en IA: {ai_error}")
            logs_analizados = valid_logs
            for log in logs_analizados:
                log['is_anomaly'] = False
                log['anomaly_score'] = 0.0
                log['ai_metadata'] = {'error': 'Fallback por fallo en IA'}

        log_entries_to_create = []
        anomalies_count = 0

        # 2. Parseo y construcción de objetos ORM
        for item in logs_analizados:
            parsed_time = parse_datetime(item.get('timestamp'))
            if not parsed_time:
                continue

            if item.get('is_anomaly', False):
                anomalies_count += 1

            log_entries_to_create.append(
                LogEntry(
                    node=node,
                    timestamp=parsed_time,
                    level=item.get('level', 'INFO'),
                    service_name=item.get('service_name', 'nginx'),
                    message=item.get('message', ''),
                    request_ip=item.get('request_ip'),
                    is_anomaly=item.get('is_anomaly', False),
                    anomaly_score=item.get('anomaly_score', 0.0),
                    ai_metadata=item.get('ai_metadata', {})
                )
            )

        # 3. Guardado masivo con transacción
        if log_entries_to_create:
            with transaction.atomic():
                LogEntry.objects.bulk_create(log_entries_to_create, batch_size=1000)

        logger.info(
            f"[Celery] Nodo={node.name} | Procesados={len(log_entries_to_create)} | "
            f"Anomalías={anomalies_count} | Ignorados={ignored_logs}"
        )

        return {
            "status": "success",
            "processed": len(log_entries_to_create),
            "anomalies": anomalies_count,
            "ignored_logs": ignored_logs
        }

    except Exception as e:
        logger.error(f"Error crítico procesando lote en Celery para nodo {node_id}: {str(e)}")
        self.retry(exc=e, countdown=10)
