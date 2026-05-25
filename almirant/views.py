import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_datetime
from .models import ServerNode, LogEntry

@csrf_exempt  # Permite que scripts externos envíen datos sin token de formulario
@require_POST
def ingest_logs(request):
    """
    Endpoint para recibir lotes de logs desde tus servidores (nodos).
    """
    try:
        data = json.loads(request.body)
        node_name = data.get('node_name')
        logs_list = data.get('logs', [])

        if not node_name:
            return JsonResponse({'error': 'Falta el parámetro node_name.'}, status=400)

        # 1. Validar que el nodo exista y esté activo en el administrador
        try:
            node = ServerNode.objects.get(name=node_name, is_active=True)
        except ServerNode.DoesNotExist:
            return JsonResponse({'error': 'ServerNode no registrado o inactivo.'}, status=403)

        # 2. Preparar la inserción masiva (Bulk Create) para cuidar el rendimiento de tu PC
        log_entries_to_create = []
        
        for log in logs_list:
            raw_timestamp = log.get('timestamp')
            parsed_timestamp = parse_datetime(raw_timestamp) if raw_timestamp else None
            
            if not parsed_timestamp:
                continue  # Si el log no tiene fecha válida, lo ignora

            log_entry = LogEntry(
                node=node,
                timestamp=parsed_timestamp,
                level=log.get('level', 'INFO'),
                service_name=log.get('service_name', 'nginx'),
                message=log.get('message', ''),
                request_ip=log.get('request_ip', None)
            )
            log_entries_to_create.append(log_entry)

        # 3. Guardar todo en una sola consulta SQL rápida
        if log_entries_to_create:
            LogEntry.objects.bulk_create(log_entries_to_create)

        return JsonResponse({
            'status': 'success',
            'received_logs': len(log_entries_to_create)
        }, status=202)  # 202 = Accepted

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)