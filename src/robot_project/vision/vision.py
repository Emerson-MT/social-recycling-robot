import time
from ultralytics import YOLO
import cv2
from collections import Counter

class ComputerVision:
    def __init__(self, model_path):
        self.cv_model = model_path
        self.load_cv_model(model_path)
    
    def load_cv_model(self, path):
        try:
            print("⏳ Cargando modelo de Computer Vision...")
            self.cv_model = YOLO(path)
            print("✅ Modelo cargado")
        except Exception as e:
            print(f"❌ Error al cargar el modelo de Computer Vision: {e}")
            raise
    
    def classify(self, tiempo_limite=3, confianza_minima=0.2):
        # Inicializar cámara
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara.")

        predicciones = []
        start_time = time.time()

        while time.time() - start_time < tiempo_limite:
            success, frame = cap.read()
            if not success:
                break

            results = self.cv_model(frame)
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]
                    confidence = float(box.conf[0])

                    # Filtrar solo predicciones válidas con confianza superior al umbral
                    if confidence > confianza_minima:
                        print(f"Detectado: {class_name} con confianza: {confidence:.2f}")
                        predicciones.append((class_id, class_name, confidence))

        cap.release()
        time.sleep(0.5)

        if predicciones:
            # Contar ocurrencias de cada clase
            nombres = [p[1] for p in predicciones]
            conteo = Counter(nombres)
            clase_mas_comun = conteo.most_common(1)[0][0]

            # Filtrar predicciones con ese nombre
            predicciones_filtradas = [p for p in predicciones if p[1] == clase_mas_comun]

            # Escoger la de mayor confianza
            prediccion_final = max(predicciones_filtradas, key=lambda x: x[2])

            return prediccion_final  # (class_id, class_name, confianza)
        else:
            return None  # No se detectó nada con confianza suficiente