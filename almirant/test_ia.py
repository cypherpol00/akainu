import os
import sys

# Script de prueba rápida para validar el detector de IA local
try:
    from ai_detector import LogAnomalyDetector
    print("🤖 Buscando modelo de IA e inicializando detector...")
    detector = LogAnomalyDetector()
    print("✅ ¡Modelo cargado en memoria exitosamente!")
except Exception as e:
    print(f"❌ Error al inicializar el detector: {e}")
    sys.exit(1)

# 1. Simulamos una lista de logs que llegaron a Akainu
logs_de_prueba = [
    {"level": "INFO", "message": "GET /home", "service_name": "cypherpol_frontend"},
    {"level": "INFO", "message": "GET /about", "service_name": "cypherpol_frontend"},
    {"level": "WARNING", "message": "GET /wp-admin.php", "service_name": "nginx_proxy"},  # Sospechoso (404)
    {"level": "INFO", "message": "POST /login", "service_name": "cypherpol_frontend"},
    {"level": "ERROR", "message": "Database connection timeout", "service_name": "postgres"}, # ¡Anomalía! (500)
]

print(f"\n⚡ Procesando {len(logs_de_prueba)} logs en lote con batch_predict()...\n")

# 2. Ejecutamos la predicción en lote
resultados = detector.batch_predict(logs_de_prueba)

# 3. Mostramos los resultados en la consola
print("-" * 70)
print(f"{'NIVEL':<10} | {'¿ES ANOMALÍA?':<14} | {'SCORE':<8} | {'MENSAJE'}")
print("-" * 70)

for log in resultados:
    alerta = "🚨 SÍ" if log['is_anomaly'] else "✅ No"
    print(f"{log['level']:<10} | {alerta:<14} | {log['anomaly_score']:<8} | {log['message']}")

print("-" * 70)
print("\n🎉 ¡Prueba ejecutada con éxito!")