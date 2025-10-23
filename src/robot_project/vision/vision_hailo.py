import cv2
import time
import numpy as np
import degirum as dg
from collections import Counter
from pprint import pprint


class HailoVision:
    def __init__(self, model_name, zoo_url='../models', inference_host='@local'):
        self.model_name = model_name
        self.zoo_url = zoo_url
        self.inference_host = inference_host
        self.model = None
        self.load_model()

    # ==============================
    # --- CARGA DEL MODELO HAILO ---
    # ==============================
    def load_model(self):
        try:
            print("⏳ Cargando modelo Hailo...")
            self.model = dg.load_model(
                model_name=self.model_name,
                inference_host_address=self.inference_host,
                zoo_url=self.zoo_url
            )
            print("✅ Modelo cargado correctamente.")
        except Exception as e:
            print(f"❌ Error al cargar el modelo Hailo: {e}")
            raise

    # =====================================================
    # --- FUNCIONES DE ESCALADO Y DIBUJO (de tu código) ---
    # =====================================================
    def resize_with_letterbox(self, image, target_shape, padding_value=(0, 0, 0)):
        """Redimensiona una imagen con letterboxing (manteniendo relación de aspecto)."""
        h, w, c = image.shape
        target_height, target_width = target_shape[1], target_shape[2]
        scale = min(target_width / w, target_height / h)

        new_w, new_h = int(w * scale), int(h * scale)
        resized_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        letterboxed_image = np.full((target_height, target_width, c), padding_value, dtype=np.uint8)

        pad_top = (target_height - new_h) // 2
        pad_left = (target_width - new_w) // 2
        letterboxed_image[pad_top:pad_top + new_h, pad_left:pad_left + new_w] = resized_image

        return letterboxed_image, scale, pad_top, pad_left

    def reverse_rescale_bboxes(self, annotations, scale, pad_top, pad_left, original_shape):
        """Convierte bounding boxes al tamaño original de la imagen."""
        orig_h, orig_w = original_shape[:2]
        new_annotations = []

        for annotation in annotations:
            x1, y1, x2, y2 = annotation['bbox']
            x1 -= pad_left; y1 -= pad_top
            x2 -= pad_left; y2 -= pad_top

            x1 = int(x1 / scale); y1 = int(y1 / scale)
            x2 = int(x2 / scale); y2 = int(y2 / scale)

            x1 = max(0, min(x1, orig_w - 1))
            y1 = max(0, min(y1, orig_h - 1))
            x2 = max(0, min(x2, orig_w - 1))
            y2 = max(0, min(y2, orig_h - 1))

            ann = annotation.copy()
            ann['bbox'] = (x1, y1, x2, y2)
            new_annotations.append(ann)

        return new_annotations

    def overlay_bboxes_and_labels(self, image, annotations, color=(0, 255, 0), font_scale=0.8, thickness=2):
        """Dibuja bounding boxes, etiquetas y confianza."""
        for ann in annotations:
            bbox = ann['bbox']
            label = ann.get('label', 'obj')
            conf = ann.get('score', None)  # puede no estar presente

            x1, y1, x2, y2 = map(int, map(round, bbox))
            cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

            # Texto: etiqueta + confianza si está disponible
            if conf is not None:
                text = f"{label}: {conf:.2f}"
            else:
                text = label

            cv2.putText(image, text, (x1, max(15, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

        return image

    # =====================================
    # --- FUNCIÓN PRINCIPAL DE DETECCIÓN ---
    # =====================================
    def classify(self, tiempo_limite=3, confianza_minima=0.3, mostrar=False):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara.")

        predicciones = []
        start_time = time.time()

        while time.time() - start_time < tiempo_limite:
            success, frame = cap.read()
            if not success:
                break

            # Preprocesamiento
            resized_image, scale, pad_top, pad_left = self.resize_with_letterbox(frame, self.model.input_shape[0])

            # Inferencia con Hailo
            inference_result = self.model(resized_image)
            detections = inference_result.results
            detections_original = self.reverse_rescale_bboxes(detections, scale, pad_top, pad_left, frame.shape)

            pprint(inference_result)

            for det in detections_original:
                class_id = det.get('category_id', 0)
                class_name = det.get('label', 'obj')
                confidence = det.get('score', 0)
                if confidence >= confianza_minima:
                    print(f"Detectado: {class_name} con confianza: {confidence:.2f}")
                    predicciones.append((class_id, class_name, confidence))

            # Mostrar resultados en pantalla (opcional)
            if mostrar:
                overlayed = self.overlay_bboxes_and_labels(frame.copy(), detections_original)
                cv2.imshow("Hailo Detection", overlayed)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()

        # Analizar resultados
        if predicciones:
            nombres = [p[1] for p in predicciones]
            conteo = Counter(nombres)
            clase_mas_comun = conteo.most_common(1)[0][0]
            pred_filtradas = [p for p in predicciones if p[1] == clase_mas_comun]
            prediccion_final = max(pred_filtradas, key=lambda x: x[2])
            return prediccion_final  # (class_id, class_name, confianza)
        else:
            return None


# =============================
# === USO DEL MÓDULO HAILO ===
# =============================
if __name__ == "__main__":
    vision = HailoVision(model_name="peri_hailo--640x640_quant_hailort_multidevice_1")

    print("🔍 Iniciando detección...")
    resultado = vision.classify(tiempo_limite=10, confianza_minima=0.3, mostrar=True)

    if resultado:
        print(f"\n✅ Resultado final: {resultado[1]} ({resultado[2]:.2f})")
    else:
        print("\n⚠️ No se detectó ningún objeto con suficiente confianza.")
