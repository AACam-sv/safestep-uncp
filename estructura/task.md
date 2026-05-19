# Implementation Plan: SafeStep UNCP

## Overview

Implementación incremental de la aplicación móvil Edge AI SafeStep UNCP en Python + Kivy. Cada tarea construye sobre la anterior, comenzando por la estructura del proyecto y los módulos core, hasta el empaquetado final como APK Android. Los archivos Python se crean con docstrings completos en español y sin lógica implementada, listos para autocompletado con GitHub Copilot CLI.

**Lenguaje:** Python 3.10+
**Framework UI:** Kivy 2.3.x
**Detección:** YOLOv8n via `ultralytics`
**Captura de video:** OpenCV (`opencv-python`)
**Testing:** `pytest` + `hypothesis`

---

## Tasks

- [ ] 1. Crear estructura de directorios y archivos de configuración del proyecto
  - Crear los directorios: `src/`, `models/`, `assets/`, `tests/`
  - Crear `src/__init__.py` vacío
  - Crear `tests/__init__.py` vacío
  - Crear `buildozer.spec` con configuración base: nombre de app `SafeStep`, paquete `org.uncp.safestep`, versión `1.0`, `android.permissions = CAMERA`, `android.minapi = 21`, requirements: `python3,kivy==2.3.0,opencv-python==4.9.0.80,ultralytics==8.2.0,numpy`, source.include_exts con `py,kv,pt,wav`, source.include_patterns con `models/yolov8n.pt,assets/*.wav`
  - Crear `requirements.txt` con versiones exactas: `kivy==2.3.0`, `opencv-python==4.9.0.80`, `ultralytics==8.2.0`, `numpy==1.26.4`, `pytest==8.2.0`, `hypothesis==6.100.0`
  - Crear archivos de audio placeholder en `assets/`: `alert_left.wav`, `alert_right.wav`, `pause.wav`, `resume.wav`, `no_camera.wav`, `no_model.wav` (archivos WAV mínimos válidos de 1 segundo)
  - Crear `models/.gitkeep` con instrucción de descarga del modelo
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1_

- [ ] 2. Implementar módulo `BoundingBox` y `Detection` (modelos de datos)
  - [ ] 2.1 Crear `src/models.py` con las dataclasses `BoundingBox` y `Detection`
    - `BoundingBox`: campos `x1`, `y1`, `x2`, `y2` (float); propiedades `center_x` y `area`; docstrings en español para cada campo y propiedad
    - `Detection`: campos `class_name` (str), `confidence` (float), `bbox` (BoundingBox); docstring en español
    - Incluir constante `VALID_CLASSES = {"person", "chair", "backpack"}`
    - Sin lógica implementada en propiedades (solo `pass` o `...`); docstrings completos
    - _Requirements: 2.2, 2.3, 3.1_

  - [ ]* 2.2 Escribir tests de propiedad para `BoundingBox` y `Detection`
    - **Property 3: Estructura válida de detecciones** — Para cualquier BoundingBox generado, verificar `x1 < x2`, `y1 < y2`, `area > 0`, `center_x == (x1+x2)/2`
    - **Property 9: Invariante de BoundingBox válido**
    - Usar `hypothesis` con estrategias `st.floats` para coordenadas
    - Archivo: `tests/test_models_property.py`
    - `# Feature: safestep-uncp, Property 3: Estructura válida de detecciones`
    - `# Feature: safestep-uncp, Property 9: Invariante de BoundingBox válido`
    - _Requirements: 2.3_

- [ ] 3. Implementar `CameraModule` (`src/camera_module.py`)
  - [ ] 3.1 Crear `src/camera_module.py` con la clase `CameraModule`
    - Métodos: `start()`, `stop()`, `read_frame()`, `is_open()`
    - Atributos internos: `_cap: Optional[cv2.VideoCapture]`, `_is_running: bool`
    - Docstrings en español para cada método: propósito, parámetros, retorno, comportamiento esperado
    - Sin lógica implementada (solo `pass`); docstrings completos
    - _Requirements: 1.1, 1.2, 1.4, 1.5_

  - [ ]* 3.2 Escribir tests unitarios para `CameraModule`
    - Mockear `cv2.VideoCapture` con `unittest.mock.MagicMock`
    - Test: `start()` llama a `cv2.VideoCapture(0)` y `is_open()` retorna `True`
    - Test: `stop()` llama a `release()` e `is_open()` retorna `False`
    - Test: `read_frame()` retorna `None` cuando la cámara no está abierta
    - Test: ciclo de vida `start() → stop() → start()` funciona correctamente (round-trip de ciclo de vida)
    - Archivo: `tests/test_camera_module.py`
    - _Requirements: 1.1, 1.4, 1.5_

- [ ] 4. Checkpoint — Verificar estructura base
  - Asegurarse de que todos los archivos creados hasta ahora existen en las rutas correctas.
  - Ejecutar `pytest tests/` y verificar que los tests existentes pasan.
  - Preguntar al usuario si hay ajustes antes de continuar.

- [ ] 5. Implementar `Detector` (`src/detector.py`)
  - [ ] 5.1 Crear `src/detector.py` con la clase `Detector`
    - Constructor: `__init__(model_path: str, confidence_threshold: float = 0.50)`; lanza `FileNotFoundError` si el archivo no existe
    - Método `detect(frame: np.ndarray) -> List[Detection]`: ejecuta inferencia YOLOv8n, filtra por `confidence_threshold` y por `VALID_CLASSES`, retorna lista de `Detection`
    - Método `is_model_loaded() -> bool`
    - Importar `Detection`, `BoundingBox`, `VALID_CLASSES` desde `src.models`
    - Docstrings en español para cada método; sin lógica implementada
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 5.2 Escribir tests unitarios para `Detector`
    - Mockear `ultralytics.YOLO` para evitar carga real del modelo
    - Test: constructor lanza `FileNotFoundError` si `model_path` no existe
    - Test: `detect()` retorna lista vacía si no hay detecciones
    - Test: `detect()` filtra detecciones con `confidence < 0.50`
    - Test: `detect()` filtra clases fuera de `VALID_CLASSES`
    - Archivo: `tests/test_detector.py`
    - _Requirements: 2.4, 2.6_

  - [ ]* 5.3 Escribir tests de propiedad para `Detector`
    - **Property 1: Invariante de clases detectadas** — Para cualquier output del Detector, `class_name ∈ {"person", "chair", "backpack"}`
    - **Property 2: Invariante de umbral de confianza** — Para cualquier output del Detector, `confidence >= 0.50`
    - Usar mocks de `ultralytics.YOLO` que retornen detecciones aleatorias generadas con `hypothesis`
    - Archivo: `tests/test_detector_property.py`
    - `# Feature: safestep-uncp, Property 1: Invariante de clases detectadas`
    - `# Feature: safestep-uncp, Property 2: Invariante de umbral de confianza`
    - _Requirements: 2.2, 2.4_

- [ ] 6. Implementar `AlertEngine` (`src/alert_engine.py`)
  - [ ] 6.1 Crear `src/alert_engine.py` con la clase `AlertEngine`
    - Constructor: `__init__(assets_path: str)`; carga archivos de audio con `SoundLoader.load()`
    - Método `process_detections(detections: List[Detection], frame_width: int) -> None`
    - Método `get_priority_detection(detections: List[Detection]) -> Optional[Detection]`
    - Método `classify_direction(bbox: BoundingBox, frame_width: int) -> str`; retorna `"left"` o `"right"`
    - Método `play_alert(direction: str) -> None`; suprime si ya se está reproduciendo la misma dirección
    - Método `play_message(message_key: str) -> None`
    - Método `is_playing() -> bool`
    - Atributos internos: `_current_alert: Optional[str]`, `_sounds: Dict[str, Any]`
    - Docstrings en español para cada método; sin lógica implementada
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]* 6.2 Escribir tests unitarios para `AlertEngine`
    - Mockear `kivy.core.audio.SoundLoader` para evitar reproducción real
    - Test: `classify_direction` retorna `"left"` cuando `center_x < frame_width/2`
    - Test: `classify_direction` retorna `"right"` cuando `center_x >= frame_width/2`
    - Test: `get_priority_detection` retorna la detección con mayor área
    - Test: `process_detections` con lista vacía no reproduce audio
    - Test: `play_alert` no reproduce si ya se está reproduciendo la misma dirección
    - Archivo: `tests/test_alert_engine.py`
    - _Requirements: 3.2, 3.3, 3.4, 4.4, 4.5_

  - [ ]* 6.3 Escribir tests de propiedad para `AlertEngine`
    - **Property 4: Clasificación direccional correcta** — Para cualquier `center_x` y `frame_width`, la clasificación es `"left"` xor `"right"` sin ambigüedad
    - **Property 5: Selección del obstáculo prioritario por área máxima** — Para cualquier lista no vacía, el prioritario tiene el área máxima
    - **Property 6: Silencio ante ausencia de obstáculos** — Para lista vacía, `is_playing()` no cambia a `True`
    - **Property 7: Supresión de alertas duplicadas** — Llamar `play_alert` dos veces con la misma dirección no inicia segunda reproducción
    - Archivo: `tests/test_alert_engine_property.py`
    - `# Feature: safestep-uncp, Property 4: Clasificación direccional correcta`
    - `# Feature: safestep-uncp, Property 5: Selección del obstáculo prioritario por área máxima`
    - `# Feature: safestep-uncp, Property 6: Silencio ante ausencia de obstáculos`
    - `# Feature: safestep-uncp, Property 7: Supresión de alertas duplicadas`
    - _Requirements: 3.2, 3.3, 3.4, 4.4, 4.5_

- [ ] 7. Checkpoint — Verificar módulos core
  - Ejecutar `pytest tests/` y verificar que todos los tests pasan.
  - Verificar que `CameraModule`, `Detector` y `AlertEngine` tienen docstrings completos en español.
  - Preguntar al usuario si hay ajustes antes de continuar.

- [ ] 8. Implementar `main.py` (`src/main.py`) — Punto de entrada Kivy
  - [ ] 8.1 Crear `src/main.py` con la clase `SafeStepApp(App)`
    - Método `build() -> Widget`: construye la UI con `CameraWidget` en pantalla completa
    - Método `on_start() -> None`: inicializa `CameraModule`, `Detector`, `AlertEngine`; maneja errores de cámara y modelo con mensajes de audio; inicia hilo de detección
    - Método `on_stop() -> None`: detiene el hilo de detección y libera la cámara
    - Método `on_pause() -> bool`: libera la cámara; retorna `True`
    - Método `on_resume() -> None`: reanuda la captura de video
    - Método `toggle_detection(touch) -> None`: alterna entre pausado/activo; reproduce audio de confirmación
    - Método `_detection_loop() -> None`: bucle en hilo de fondo; lee frames, detecta, alerta
    - Atributos: `_camera: CameraModule`, `_detector: Detector`, `_alert_engine: AlertEngine`, `_is_detecting: bool`, `_thread: threading.Thread`
    - Docstrings en español para cada método; sin lógica implementada
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 2.6, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 8.2 Escribir tests unitarios para `main.py`
    - Mockear `CameraModule`, `Detector`, `AlertEngine` con `unittest.mock.MagicMock`
    - Test: `on_start()` reproduce `no_camera.wav` si `CameraModule.is_open()` retorna `False`
    - Test: `on_start()` reproduce `no_model.wav` si `Detector.__init__` lanza `FileNotFoundError`
    - Test: `toggle_detection()` cambia `_is_detecting` de `True` a `False`
    - Test: `toggle_detection()` cambia `_is_detecting` de `False` a `True`
    - Archivo: `tests/test_main.py`
    - _Requirements: 1.3, 2.6, 5.3, 5.4, 5.5_

  - [ ]* 8.3 Escribir test de propiedad para toggle de detección
    - **Property 8: Toggle de detección (round-trip)** — Para cualquier estado inicial, aplicar `toggle_detection` dos veces retorna al estado original
    - Archivo: `tests/test_main_property.py`
    - `# Feature: safestep-uncp, Property 8: Toggle de detección (round-trip)`
    - _Requirements: 5.3_

- [ ] 9. Crear documentación: `README.md` y `ARQUITECTURA.md`
  - [ ] 9.1 Crear `README.md` en la raíz del proyecto con las siguientes secciones:
    - **Descripción del proyecto**: SafeStep UNCP, propósito, tecnologías
    - **Instalación y ejecución local**: `pip install -r requirements.txt`, `python src/main.py`
    - **Compilación del APK**: pasos con Buildozer (`buildozer android debug`)
    - **Re-entrenamiento del modelo con Azure Machine Learning**:
      - Configurar workspace AML (portal Azure o CLI)
      - Formato de dataset YOLO: estructura de directorios `images/train/`, `images/val/`, `labels/train/`, `labels/val/`; archivos `.txt` con formato `<class_id> <x_center> <y_center> <width> <height>` normalizados
      - Comando de entrenamiento: `yolo train model=yolov8n.pt data=dataset.yaml epochs=50 imgsz=640`
      - Exportar modelo re-entrenado: `yolo export model=runs/detect/train/weights/best.pt format=torchscript`
      - Reemplazar `models/yolov8n.pt` con el modelo exportado
    - _Requirements: 7.7, 8.1, 8.2, 8.3, 8.4_

  - [ ] 9.2 Crear `ARQUITECTURA.md` en la raíz del proyecto con las siguientes secciones:
    - **Diagrama de componentes**: descripción textual y diagrama ASCII del pipeline Camera → Detector → AlertEngine
    - **Flujo de datos**: descripción del ciclo frame → detección → clasificación → audio
    - **Decisiones de diseño técnico**: justificación de YOLOv8n (tamaño/velocidad), Kivy (cross-platform), OpenCV (captura), Edge AI (privacidad/offline)
    - **Estructura de directorios**: árbol de archivos del proyecto
    - _Requirements: 8.5_

- [ ] 10. Checkpoint — Verificar documentación y estructura completa
  - Verificar que `README.md` contiene todas las secciones requeridas (AML, formato dataset, comando de entrenamiento).
  - Verificar que `ARQUITECTURA.md` describe el flujo de datos y las decisiones de diseño.
  - Ejecutar `pytest tests/` y verificar que todos los tests pasan.
  - Preguntar al usuario si hay ajustes antes de continuar.

- [ ] 11. Crear archivo `.kiro/specs/safestep-uncp/.config.kiro` (configuración del spec)
  - Crear el archivo con contenido: `{"specId": "aebc2a68-4c19-4ad2-9172-1a2485ca1362", "workflowType": "requirements-first", "specType": "feature"}`
  - _Requirements: (configuración interna del spec)_

- [ ] 12. Integración final: conectar todos los módulos en `main.py`
  - [ ] 12.1 Implementar el bucle `_detection_loop()` en `src/main.py`
    - Leer frame con `CameraModule.read_frame()`
    - Si el frame es `None`, continuar al siguiente ciclo
    - Llamar a `Detector.detect(frame)` para obtener detecciones
    - Llamar a `AlertEngine.process_detections(detections, frame_width)` para emitir alerta
    - Controlar la frecuencia del bucle para mantener ≥15 FPS (sleep de ~66ms)
    - Respetar el flag `_is_detecting` para pausar/reanudar
    - _Requirements: 1.2, 2.1, 3.1, 4.1, 4.2, 5.3_

  - [ ] 12.2 Implementar el widget de cámara en `src/main.py`
    - Crear `CameraWidget(Widget)` que muestre el feed de la cámara en pantalla completa usando `Kivy Image` o `Texture`
    - Vincular el evento `on_touch_down` al método `toggle_detection`
    - _Requirements: 5.2, 5.3_

  - [ ]* 12.3 Escribir test de integración del pipeline completo
    - Crear `tests/test_integration.py`
    - Test: dado un frame de prueba estático (imagen numpy), el pipeline completo retorna una dirección válida (`"left"` o `"right"`) o silencio (lista vacía)
    - Usar mocks para `ultralytics.YOLO` y `SoundLoader`
    - _Requirements: 2.1, 3.1, 4.1, 4.2, 4.5_

- [ ] 13. Checkpoint final — Verificar implementación completa
  - Ejecutar `pytest tests/ -v` y verificar que todos los tests pasan (unitarios, de propiedad e integración).
  - Verificar que todos los archivos Python tienen docstrings en español en cada función y clase.
  - Verificar que `buildozer.spec` contiene `CAMERA` en permisos y todas las dependencias con versiones exactas.
  - Verificar que `models/` contiene instrucciones para descargar `yolov8n.pt`.
  - Preguntar al usuario si hay ajustes finales antes de proceder con la compilación del APK.

---

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido.
- Todos los archivos Python deben crearse **sin lógica implementada** (solo `pass` o `...` en el cuerpo de las funciones), con docstrings completos en español, para uso con GitHub Copilot CLI.
- Los tests de propiedad requieren `hypothesis` instalado (`pip install hypothesis`).
- Para compilar el APK se requiere Buildozer en Linux/WSL: `pip install buildozer` y luego `buildozer android debug` desde la raíz del proyecto.
- El archivo `models/yolov8n.pt` debe descargarse manualmente antes de ejecutar la app: `python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"` y mover el archivo a `models/`.
- Cada tarea de test de propiedad referencia explícitamente la propiedad del diseño con el formato: `# Feature: safestep-uncp, Property N: <texto>`.
