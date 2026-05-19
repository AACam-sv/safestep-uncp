# Requirements Document

## Introduction

SafeStep UNCP es una aplicación móvil de Edge AI diseñada para estudiantes con discapacidad visual de la Universidad Nacional del Centro del Perú (UNCP). La aplicación captura video en tiempo real desde la cámara del dispositivo móvil, procesa cada fotograma con un modelo YOLOv8n para detectar obstáculos relevantes en el entorno universitario (personas, sillas, mochilas), y emite alertas de audio direccionales (izquierda o derecha) para guiar al usuario de forma segura. Todo el procesamiento ocurre en el dispositivo (Edge AI), sin requerir conexión a internet durante el uso.

---

## Glossary

- **SafeStep_App**: La aplicación móvil Android desarrollada con Kivy y Python.
- **Detector**: El módulo de detección de objetos basado en YOLOv8n que analiza fotogramas de video.
- **Alert_Engine**: El módulo responsable de generar y reproducir alertas de audio direccionales.
- **Camera_Module**: El módulo que gestiona la captura de video desde la cámara del dispositivo usando OpenCV.
- **Frame**: Un fotograma individual capturado por la cámara del dispositivo.
- **Bounding_Box**: El rectángulo delimitador que el Detector asigna a cada objeto detectado en un Frame.
- **Obstacle**: Un objeto detectado perteneciente a las clases: persona, silla o mochila.
- **Confidence_Score**: El valor numérico entre 0.0 y 1.0 que el Detector asigna a cada detección indicando su certeza.
- **Directional_Alert**: Una señal de audio que indica si el Obstacle se encuentra a la izquierda o a la derecha del centro del Frame.
- **Model_File**: El archivo de pesos del modelo YOLOv8n (`yolov8n.pt`) almacenado localmente en el dispositivo.
- **Buildozer**: La herramienta de empaquetado que compila el proyecto Python/Kivy en un archivo APK para Android.
- **APK**: El paquete de instalación de la aplicación para dispositivos Android.
- **AML**: Azure Machine Learning, plataforma usada para el re-entrenamiento futuro del modelo.

---

## Requirements

### Requirement 1: Captura de Video en Tiempo Real

**User Story:** Como estudiante con discapacidad visual de la UNCP, quiero que la aplicación capture video continuamente desde la cámara de mi celular, para que el sistema pueda analizar mi entorno en tiempo real.

#### Acceptance Criteria

1. WHEN la SafeStep_App es iniciada por el usuario, THE Camera_Module SHALL abrir la cámara trasera del dispositivo y comenzar la captura de video.
2. WHILE la SafeStep_App está en ejecución en primer plano, THE Camera_Module SHALL capturar Frames a una tasa mínima de 15 fotogramas por segundo.
3. IF la cámara del dispositivo no está disponible o el permiso CAMERA ha sido denegado, THEN THE SafeStep_App SHALL reproducir un mensaje de audio notificando al usuario que la cámara no está accesible.
4. WHEN la SafeStep_App pasa a segundo plano, THE Camera_Module SHALL liberar el recurso de la cámara del dispositivo.
5. WHEN la SafeStep_App regresa al primer plano, THE Camera_Module SHALL reanudar la captura de video automáticamente.

---

### Requirement 2: Detección de Obstáculos con YOLOv8n

**User Story:** Como estudiante con discapacidad visual, quiero que la aplicación identifique obstáculos comunes en el campus universitario, para que pueda navegar de forma segura por pasillos y aulas.

#### Acceptance Criteria

1. WHEN un Frame es capturado por el Camera_Module, THE Detector SHALL procesar el Frame usando el Model_File para identificar Obstacles.
2. THE Detector SHALL detectar Obstacles de las siguientes clases: persona (`person`), silla (`chair`) y mochila (`backpack`).
3. WHEN el Detector procesa un Frame, THE Detector SHALL retornar la lista de Bounding_Boxes con su clase y Confidence_Score asociados.
4. THE Detector SHALL descartar detecciones cuyo Confidence_Score sea inferior a 0.50.
5. THE Detector SHALL procesar cada Frame en un tiempo máximo de 500 milisegundos en el dispositivo objetivo.
6. IF el Model_File no se encuentra en la ruta configurada al iniciar la SafeStep_App, THEN THE SafeStep_App SHALL reproducir un mensaje de audio notificando al usuario que el modelo de detección no está disponible.
7. THE Detector SHALL operar completamente en el dispositivo sin requerir conexión a internet.

---

### Requirement 3: Determinación de Dirección del Obstáculo

**User Story:** Como estudiante con discapacidad visual, quiero saber si un obstáculo está a mi izquierda o a mi derecha, para que pueda esquivarlo sin necesidad de ver la pantalla.

#### Acceptance Criteria

1. WHEN el Detector retorna al menos un Bounding_Box, THE Alert_Engine SHALL calcular la posición horizontal del centro de cada Bounding_Box relativa al centro horizontal del Frame.
2. WHEN el centro horizontal de un Bounding_Box es menor que el 50% del ancho del Frame, THE Alert_Engine SHALL clasificar el Obstacle como ubicado a la izquierda.
3. WHEN el centro horizontal de un Bounding_Box es mayor o igual al 50% del ancho del Frame, THE Alert_Engine SHALL clasificar el Obstacle como ubicado a la derecha.
4. WHEN múltiples Obstacles son detectados en el mismo Frame, THE Alert_Engine SHALL priorizar el Obstacle cuyo Bounding_Box tenga el mayor área, considerándolo el más cercano.
5. THE Alert_Engine SHALL calcular la dirección del Obstacle prioritario en un tiempo máximo de 10 milisegundos.

---

### Requirement 4: Emisión de Alertas de Audio Direccionales

**User Story:** Como estudiante con discapacidad visual, quiero recibir alertas de audio que me indiquen la dirección del obstáculo, para que pueda reaccionar a tiempo sin depender de la pantalla.

#### Acceptance Criteria

1. WHEN el Alert_Engine clasifica un Obstacle como ubicado a la izquierda, THE Alert_Engine SHALL reproducir el archivo de audio de alerta izquierda almacenado en `assets/`.
2. WHEN el Alert_Engine clasifica un Obstacle como ubicado a la derecha, THE Alert_Engine SHALL reproducir el archivo de audio de alerta derecha almacenado en `assets/`.
3. THE Alert_Engine SHALL reproducir la Directional_Alert en un tiempo máximo de 200 milisegundos desde la clasificación del Obstacle.
4. WHILE una Directional_Alert está siendo reproducida, THE Alert_Engine SHALL suprimir nuevas alertas del mismo tipo para evitar superposición de audio.
5. IF no se detectan Obstacles en un Frame, THEN THE Alert_Engine SHALL permanecer en silencio y no reproducir ningún audio.
6. THE Alert_Engine SHALL utilizar únicamente archivos de audio almacenados localmente en el dispositivo, sin requerir conexión a internet.

---

### Requirement 5: Interfaz de Usuario Accesible

**User Story:** Como estudiante con discapacidad visual, quiero que la aplicación sea operable con el mínimo de interacción táctil, para que pueda usarla de forma autónoma sin necesidad de ver la pantalla.

#### Acceptance Criteria

1. THE SafeStep_App SHALL iniciar el modo de detección automáticamente al abrirse, sin requerir interacción táctil del usuario.
2. THE SafeStep_App SHALL mostrar la vista de la cámara en pantalla completa como única pantalla principal.
3. WHEN el usuario toca la pantalla una vez, THE SafeStep_App SHALL pausar o reanudar la detección de Obstacles alternadamente.
4. WHEN la SafeStep_App pausa la detección, THE Alert_Engine SHALL reproducir un mensaje de audio confirmando la pausa.
5. WHEN la SafeStep_App reanuda la detección, THE Alert_Engine SHALL reproducir un mensaje de audio confirmando la reanudación.
6. THE SafeStep_App SHALL ser empaquetada como un APK instalable en dispositivos Android con versión mínima de API 21 (Android 5.0).

---

### Requirement 6: Empaquetado y Distribución como APK

**User Story:** Como desarrollador del proyecto, quiero compilar la aplicación como un APK de Android, para que los estudiantes de la UNCP puedan instalarla directamente en sus dispositivos.

#### Acceptance Criteria

1. THE Buildozer SHALL generar un archivo APK funcional a partir del código fuente del proyecto usando el archivo `buildozer.spec`.
2. THE `buildozer.spec` SHALL declarar el permiso `android.permissions = CAMERA` para que el sistema operativo Android conceda acceso a la cámara.
3. THE `buildozer.spec` SHALL incluir todas las dependencias necesarias: `kivy`, `opencv-python`, `ultralytics`, y sus dependencias transitivas.
4. THE APK SHALL incluir el Model_File (`yolov8n.pt`) empaquetado dentro del directorio `models/` de la aplicación.
5. THE APK SHALL incluir los archivos de audio de alerta empaquetados dentro del directorio `assets/` de la aplicación.
6. IF el proceso de compilación con Buildozer falla por una dependencia faltante, THEN el `buildozer.spec` SHALL especificar la versión exacta de cada dependencia para garantizar reproducibilidad.

---

### Requirement 7: Estructura del Proyecto y Preparación para Copilot CLI

**User Story:** Como desarrollador, quiero que el código fuente esté estructurado con docstrings y comentarios detallados, para que GitHub Copilot CLI pueda autocompletar la lógica de cada función de forma precisa.

#### Acceptance Criteria

1. THE SafeStep_App SHALL organizar el código fuente en los directorios: `src/` para módulos Python, `models/` para el Model_File, y `assets/` para archivos de audio.
2. THE SafeStep_App SHALL contener un archivo `src/main.py` como punto de entrada de la aplicación Kivy.
3. THE SafeStep_App SHALL contener un archivo `src/detector.py` con la clase `Detector` que encapsula la lógica de inferencia YOLOv8.
4. THE SafeStep_App SHALL contener un archivo `src/alert_engine.py` con la clase `AlertEngine` que encapsula la lógica de audio direccional.
5. THE SafeStep_App SHALL contener un archivo `src/camera_module.py` con la clase `CameraModule` que encapsula la captura de video con OpenCV.
6. WHEN un archivo Python del proyecto es creado, THE SafeStep_App SHALL incluir en cada función un docstring en español que describa: propósito, parámetros, valor de retorno y comportamiento esperado.
7. THE SafeStep_App SHALL incluir un archivo `README.md` en la raíz del proyecto que documente el proceso de re-entrenamiento del modelo usando Azure Machine Learning (AML).

---

### Requirement 8: Re-entrenamiento del Modelo (Documentación)

**User Story:** Como desarrollador, quiero documentar el proceso de re-entrenamiento del modelo YOLOv8n con datos del campus de la UNCP, para que el equipo pueda mejorar la precisión de detección en el futuro usando créditos de Azure Machine Learning.

#### Acceptance Criteria

1. THE `README.md` SHALL describir los pasos para configurar un workspace de Azure Machine Learning para re-entrenar el modelo YOLOv8n.
2. THE `README.md` SHALL especificar el formato de dataset requerido (YOLO format: imágenes + archivos `.txt` de anotaciones) para el re-entrenamiento.
3. THE `README.md` SHALL documentar el comando de entrenamiento de Ultralytics CLI para iniciar el re-entrenamiento desde AML.
4. THE `README.md` SHALL describir cómo exportar el modelo re-entrenado y reemplazar el `yolov8n.pt` en el directorio `models/` del proyecto.
5. THE SafeStep_App SHALL incluir un archivo `ARQUITECTURA.md` que describa la arquitectura de componentes del sistema, el flujo de datos entre módulos y las decisiones de diseño técnico.
