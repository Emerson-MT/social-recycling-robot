import time
import cv2
import numpy as np
from collections import Counter
from enum import Enum

# Intentar importar dependencias de Hailo
try:
    from hailo_platform import (VDevice, HailoStreamInterface,
                                ConfigureParams, InferVStreams,
                                InputVStreamParams, OutputVStreamParams)
    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False
    print("⚠️  Advertencia: Hailo no disponible. Instala 'pip install hailort hailo-platform'")

# Fallback a YOLO estándar si Hailo no está disponible
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


class ModelFormat(Enum):
    """Formatos de modelo soportados"""
    HEF = "hef"      # Hailo Executable Format (recomendado)
    ONNX = "onnx"    # ONNX con conversión runtime
    PT = "pt"        # PyTorch (fallback sin Hailo)


class ComputerVisionHailo:
    """
    Clase de Computer Vision optimizada para Hailo-8L en Raspberry Pi 5.

    Soporta múltiples modos de operación:
    - HEF (Hailo Executable Format): Máximo rendimiento, modelo pre-compilado
    - ONNX: Requiere conversión runtime a HEF (más lento en inicialización)
    - PT (fallback): Usa Ultralytics YOLO si Hailo no está disponible

    Args:
        model_path (str): Ruta al archivo del modelo (.hef, .onnx, o .pt)
        use_hailo (bool): Si False, fuerza usar Ultralytics YOLO (para debugging)
        model_format (ModelFormat): Formato del modelo (auto-detectado si es None)
        class_names (dict): Mapeo de class_id -> nombre (ej: {0: "cartón", 1: "papel"})
    """

    def __init__(self, model_path, use_hailo=True, model_format=None, class_names=None):
        self.model_path = model_path
        self.use_hailo = use_hailo and HAILO_AVAILABLE
        self.model_format = model_format or self._detect_format(model_path)

        # Nombres de clases por defecto (4 clases de reciclaje)
        self.class_names = class_names or {
            0: "cartón",
            1: "papel",
            2: "plástico",
            3: "residuo_general"
        }

        # Variables para Hailo
        self.vdevice = None
        self.network_group = None
        self.network_params = None
        self.input_vstreams = None
        self.output_vstreams = None

        # Variable para fallback YOLO
        self.yolo_model = None

        # Cargar modelo según configuración
        self.load_model()

    def _detect_format(self, path):
        """Auto-detecta el formato del modelo por extensión"""
        if path.endswith('.hef'):
            return ModelFormat.HEF
        elif path.endswith('.onnx'):
            return ModelFormat.ONNX
        elif path.endswith('.pt'):
            return ModelFormat.PT
        else:
            raise ValueError(f"Formato de modelo no reconocido: {path}")

    def load_model(self):
        """Carga el modelo según el formato y disponibilidad de hardware"""
        try:
            if self.use_hailo and self.model_format in [ModelFormat.HEF, ModelFormat.ONNX]:
                self._load_hailo_model()
            elif self.model_format == ModelFormat.PT or not self.use_hailo:
                self._load_yolo_model()
            else:
                raise RuntimeError("No se puede cargar el modelo: Hailo no disponible y modelo no es .pt")
        except Exception as e:
            print(f"❌ Error al cargar modelo: {e}")
            raise

    def _load_hailo_model(self):
        """Carga modelo usando Hailo NPU"""
        if not HAILO_AVAILABLE:
            raise RuntimeError("Hailo no está instalado. Usa: pip install hailort hailo-platform")

        print(f"⏳ Cargando modelo Hailo ({self.model_format.value})...")

        try:
            # Crear dispositivo virtual Hailo
            params = VDevice.create_params()
            self.vdevice = VDevice(params)

            # Si es ONNX, necesitamos compilarlo primero (esto es lento)
            if self.model_format == ModelFormat.ONNX:
                print("⚠️  Modelo ONNX detectado. Compilando a HEF...")
                print("    Esto puede tardar varios minutos la primera vez.")
                print("    Considera pre-compilar con: hailomz compile --ckpt tu_modelo.onnx")
                # Nota: La compilación runtime requiere hailo-model-zoo
                # En producción es mejor usar modelos .hef pre-compilados
                self._compile_onnx_to_hef()

            # Configurar red neuronal desde HEF
            hef_path = self.model_path if self.model_format == ModelFormat.HEF else self.compiled_hef_path

            network_groups = self.vdevice.configure(
                ConfigureParams.create_from_hef(hef_path, interface=HailoStreamInterface.PCIe)
            )
            self.network_group = network_groups[0]
            self.network_params = self.network_group.create_params()

            # Crear streams de entrada/salida
            input_vstreams_params = InputVStreamParams.make_from_network_group(
                self.network_group,
                quantized=False,
                format_type=None
            )
            output_vstreams_params = OutputVStreamParams.make_from_network_group(
                self.network_group,
                quantized=False,
                format_type=None
            )

            self.input_vstreams = InferVStreams(self.network_group, input_vstreams_params)
            self.output_vstreams = InferVStreams(self.network_group, output_vstreams_params)

            print("✅ Modelo Hailo cargado exitosamente")
            print(f"   Hardware: Hailo-8L (13 TOPS)")
            print(f"   Formato: {self.model_format.value}")

        except Exception as e:
            print(f"❌ Error cargando modelo Hailo: {e}")
            print("    Intentando fallback a YOLO...")
            self.use_hailo = False
            self._load_yolo_model()

    def _compile_onnx_to_hef(self):
        """Compila modelo ONNX a HEF usando Hailo Model Zoo"""
        try:
            import subprocess
            import os

            output_hef = self.model_path.replace('.onnx', '.hef')

            # Verificar si ya existe el HEF compilado
            if os.path.exists(output_hef):
                print(f"   ✓ Usando HEF pre-compilado: {output_hef}")
                self.compiled_hef_path = output_hef
                self.model_format = ModelFormat.HEF
                return

            # Compilar con hailomz
            cmd = [
                "hailomz", "compile",
                "--ckpt", self.model_path,
                "--hw-arch", "hailo8l",
                "--classes", str(len(self.class_names)),
                "--performance"
            ]

            print(f"   Ejecutando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode != 0:
                raise RuntimeError(f"Compilación falló: {result.stderr}")

            self.compiled_hef_path = output_hef
            self.model_format = ModelFormat.HEF
            print(f"   ✓ Modelo compilado: {output_hef}")

        except FileNotFoundError:
            raise RuntimeError(
                "hailomz no encontrado. Instala: pip install hailo-model-zoo\n"
                "O pre-compila tu modelo ONNX a HEF manualmente."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Compilación excedió timeout de 10 minutos")

    def _load_yolo_model(self):
        """Carga modelo usando Ultralytics YOLO (fallback)"""
        if not ULTRALYTICS_AVAILABLE:
            raise RuntimeError("Ultralytics no disponible. Instala: pip install ultralytics")

        print("⏳ Cargando modelo YOLO (modo fallback)...")
        self.yolo_model = YOLO(self.model_path)
        print("✅ Modelo YOLO cargado")
        print("   ⚠️  Ejecutando en CPU/GPU, no usando Hailo NPU")

    def _preprocess_frame(self, frame):
        """Preprocesa frame para inferencia Hailo"""
        # Obtener tamaño de entrada del modelo (típicamente 640x640 para YOLO)
        input_shape = self.input_vstreams.get_input_shape()
        height, width = input_shape[0], input_shape[1]

        # Resize manteniendo aspect ratio (letterbox)
        resized = cv2.resize(frame, (width, height))

        # Normalizar a [0, 1] y convertir a float32
        normalized = resized.astype(np.float32) / 255.0

        # Cambiar de HWC a CHW (Channels, Height, Width)
        transposed = np.transpose(normalized, (2, 0, 1))

        # Agregar dimensión de batch
        batched = np.expand_dims(transposed, axis=0)

        return batched

    def _postprocess_hailo_output(self, output_data):
        """
        Post-procesa salida de Hailo.
        Nota: Si el modelo HEF tiene NMS integrado, la salida ya está filtrada.
        """
        detections = []

        # El formato de salida depende de si el HEF tiene NMS o no
        # Formato típico con NMS: [num_detections, 6] donde cada fila es:
        # [x1, y1, x2, y2, confidence, class_id]

        try:
            # Obtener el primer tensor de salida
            output_tensor = list(output_data.values())[0]

            # Si el tensor tiene forma [1, N, 6], aplanar
            if len(output_tensor.shape) == 3:
                output_tensor = output_tensor[0]

            for detection in output_tensor:
                if len(detection) >= 6:
                    x1, y1, x2, y2, conf, class_id = detection[:6]

                    # Convertir class_id a int
                    class_id = int(class_id)

                    # Obtener nombre de clase
                    class_name = self.class_names.get(class_id, f"clase_{class_id}")

                    detections.append((class_id, class_name, float(conf)))

        except Exception as e:
            print(f"⚠️  Error en post-procesamiento: {e}")
            # Retornar lista vacía en caso de error
            return []

        return detections

    def _infer_hailo(self, frame):
        """Ejecuta inferencia usando Hailo NPU"""
        # Preprocesar frame
        input_data = self._preprocess_frame(frame)

        # Crear diccionario de entrada
        input_dict = {list(self.input_vstreams.keys())[0]: input_data}

        # Ejecutar inferencia
        with self.network_group.activate(self.network_params):
            output_dict = self.input_vstreams.infer(input_dict)

        # Post-procesar salida
        detections = self._postprocess_hailo_output(output_dict)

        return detections

    def _infer_yolo(self, frame):
        """Ejecuta inferencia usando YOLO (fallback)"""
        detections = []

        results = self.yolo_model(frame, verbose=False)
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = float(box.conf[0])

                detections.append((class_id, class_name, confidence))

        return detections

    def classify(self, tiempo_limite=3, confianza_minima=0.2):
        """
        Clasifica residuos usando votación temporal sobre múltiples frames.

        Args:
            tiempo_limite (int): Segundos de captura de video
            confianza_minima (float): Umbral mínimo de confianza [0.0-1.0]

        Returns:
            tuple: (class_id, class_name, confidence) o None si no detecta nada
        """
        # Inicializar cámara
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara.")

        predicciones = []
        start_time = time.time()
        frame_count = 0

        print(f"🎥 Iniciando clasificación ({tiempo_limite}s)...")

        while time.time() - start_time < tiempo_limite:
            success, frame = cap.read()
            if not success:
                break

            frame_count += 1

            # Ejecutar inferencia según el backend
            if self.use_hailo:
                detections = self._infer_hailo(frame)
            else:
                detections = self._infer_yolo(frame)

            # Filtrar por confianza
            for detection in detections:
                class_id, class_name, confidence = detection

                if confidence > confianza_minima:
                    print(f"   Detectado: {class_name} ({confidence:.2%})")
                    predicciones.append(detection)

        cap.release()
        time.sleep(0.5)

        print(f"📊 Procesados {frame_count} frames, {len(predicciones)} detecciones válidas")

        if predicciones:
            # Contar ocurrencias de cada clase
            nombres = [p[1] for p in predicciones]
            conteo = Counter(nombres)
            clase_mas_comun = conteo.most_common(1)[0][0]

            print(f"🗳️  Votación: {dict(conteo)}")

            # Filtrar predicciones con ese nombre
            predicciones_filtradas = [p for p in predicciones if p[1] == clase_mas_comun]

            # Escoger la de mayor confianza
            prediccion_final = max(predicciones_filtradas, key=lambda x: x[2])

            print(f"✅ Resultado final: {prediccion_final[1]} ({prediccion_final[2]:.2%})")
            return prediccion_final  # (class_id, class_name, confianza)
        else:
            print("❌ No se detectó nada con confianza suficiente")
            return None  # No se detectó nada con confianza suficiente

    def __del__(self):
        """Limpia recursos al destruir el objeto"""
        if self.vdevice is not None:
            try:
                self.vdevice.release()
            except:
                pass


# Mantener compatibilidad con código existente
class ComputerVision:
    """
    Clase legacy para compatibilidad con código antiguo.
    Redirige a ComputerVisionHailo con auto-detección.
    """
    def __init__(self, model_path):
        print("⚠️  Usando clase ComputerVision legacy")
        print("    Considera migrar a ComputerVisionHailo para mejor control")

        # Auto-detectar si debe usar Hailo
        use_hailo = model_path.endswith(('.hef', '.onnx'))

        self.cv_engine = ComputerVisionHailo(
            model_path=model_path,
            use_hailo=use_hailo
        )

    def classify(self, tiempo_limite=3, confianza_minima=0.2):
        return self.cv_engine.classify(tiempo_limite, confianza_minima)
