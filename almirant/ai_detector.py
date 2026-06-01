import os
import joblib
import numpy as np
import warnings

# Silenciamos las advertencias de nombres de columnas y versiones para que no ensucien tu consola
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")

class LogAnomalyDetector:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'models/detector_v1.joblib')
        try:
            self.model = joblib.load(self.model_path)
        except Exception as e:
            raise RuntimeError(f"Error cargando modelo: {e}")
        
        self.level_map = {'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}

    def _prepare_features(self, level: str) -> tuple[int, int]:
        """Convierte el nivel en features numéricas (status_code, level_num)."""
        level_upper = level.upper()
        level_num = self.level_map.get(level_upper, 1)

        status_code = 200
        if level_upper in ['ERROR', 'CRITICAL']:
            status_code = 500
        elif level_upper == 'WARNING':
            status_code = 404

        return status_code, level_num

    def predict_anomaly(self, level: str, message: str, service_name: str) -> tuple[bool, float, dict]:
        status_code, level_num = self._prepare_features(level)
        
        # Usamos un array de Numpy puro (cero descargas, ultra rápido)
        X_test = np.array([[status_code, level_num]])

        decision_score = self.model.decision_function(X_test)[0]
        
        # Si el score matemático es menor a 0, es una anomalía real (así evitamos el choque de versiones)
        is_anomaly = decision_score < 0
        anomaly_score = float(np.round(1 / (1 + np.exp(decision_score)), 4))

        ai_metadata = {
            "detector_version": "isolation_forest_v1_numpy",
            "raw_decision_score": float(decision_score)
        }

        return is_anomaly, anomaly_score, ai_metadata

    def batch_predict(self, logs: list[dict]) -> list[dict]:
        if not logs:
            return []

        results = []
        features = []

        for log in logs:
            status_code, level_num = self._prepare_features(log['level'])
            features.append([status_code, level_num])

        # Convertimos la lista de lotes a Numpy completo
        X_batch = np.array(features)

        decision_scores = self.model.decision_function(X_batch)

        for log, score in zip(logs, decision_scores):
            is_anomaly = score < 0
            anomaly_score = float(np.round(1 / (1 + np.exp(score)), 4))

            results.append({
                "level": log['level'],
                "message": log['message'],
                "service_name": log['service_name'],
                "is_anomaly": is_anomaly,
                "anomaly_score": anomaly_score,
                "raw_decision_score": float(score)
            })

        return results