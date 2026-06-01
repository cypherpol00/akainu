import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ServerNode
from .utils import preprocess_logs
from .tasks import process_logs_task

logger = logging.getLogger(__name__)
MAX_LOGS_PER_REQUEST = 10000

@csrf_exempt
@require_POST
def ingest_logs(request):
    """
    Endpoint Enterprise: recibe logs y delega procesamiento a Celery.
    """
    try:
        if request.headers.get("Content-Type") != "application/json":
            return JsonResponse({'error': 'Content-Type debe ser application/json.'}, status=415)

        data = json.loads(request.body.decode("utf-8"))
        node_name = data.get('node_name')
        logs_list = data.get('logs', [])

        if not node_name:
            return JsonResponse({'error': 'Falta el parámetro node_name.'}, status=400)

        if not isinstance(logs_list, list):
            return JsonResponse({'error': 'El campo logs debe ser una lista.'}, status=400)

        if len(logs_list) > MAX_LOGS_PER_REQUEST:
            return JsonResponse({'error': f'Límite de {MAX_LOGS_PER_REQUEST} logs excedido.'}, status=413)

        # Validar nodo
        try:
            node = ServerNode.objects.get(name=node_name, is_active=True)
        except ServerNode.DoesNotExist:
            return JsonResponse({'error': 'ServerNode no registrado o inactivo.'}, status=403)

        # Preprocesar logs
        valid_logs, ignored_logs = preprocess_logs(logs_list)
        if not valid_logs:
            return JsonResponse({'status': 'no_data', 'ignored_logs': ignored_logs}, status=200)

        # Encolar tarea Celery
        task = process_logs_task.delay(node.id, valid_logs, ignored_logs)

        return JsonResponse({
            'status': 'accepted',
            'task_id': task.id,
            'received_logs': len(valid_logs),
            'ignored_logs': ignored_logs
        }, status=202)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido.'}, status=400)
    except Exception as e:
        logger.exception("Error interno crítico en ingest_logs")
        return JsonResponse({'error': 'Error interno en el servidor.'}, status=500)

