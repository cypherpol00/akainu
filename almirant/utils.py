# almirant/utils.py
import logging

logger = logging.getLogger(__name__)

def preprocess_logs(logs_list):
    """
    Filtra y limpia la lista de logs recibida por la API.
    Asegura que los campos obligatorios existan y mantiene 
    los timestamps como strings puros para la serialización de Celery.
    """
    valid_logs = []
    ignored_logs = 0

    for log in logs_list:
        # Validamos que al menos venga el mensaje y la estampa de tiempo
        raw_timestamp = log.get('timestamp')
        message = log.get('message')

        if not raw_timestamp or message is None:
            ignored_logs += 1
            continue

        # Limpiamos y estructuramos manteniendo tipos de datos JSON estándar (strings, ints)
        valid_logs.append({
            'timestamp': raw_timestamp,  # Se queda como string, Celery lo parseará después
            'level': log.get('level', 'INFO').upper(),
            'service_name': log.get('service_name', 'nginx'),
            'message': message,
            'request_ip': log.get('request_ip', None)
        })

    return valid_logs, ignored_logs