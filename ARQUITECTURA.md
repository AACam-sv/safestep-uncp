# Arquitectura de SafeStep UNCP

## Diagrama de componentes

```
┌───────────────────────────────────────────┐
│            SafeStep (Kivy App)            │
│                                           │
│  ┌──────────────┐   Frames   ┌──────────┐ │
│  │ CameraModule │ ─────────► │ Detector │ │
│  │   (OpenCV)   │           │ (YOLOv8n)│ │
│  └──────────────┘           └────┬─────┘ │
│                                  │       │
│                                  ▼       │
│                           ┌──────────┐   │
│                           │AlertEngine│  │
│                           │ (Audio)  │   │
│                           └──────────┘   │
└───────────────────────────────────────────┘
```

## Flujo de datos
1. La cámara captura un frame con OpenCV.
2. El detector YOLOv8n procesa el frame y obtiene detecciones.
3. El motor de alertas elige el obstáculo prioritario y decide izquierda/derecha.
4. Se reproduce el audio correspondiente.
5. Se envía un POST HTTP con las clases detectadas.

## Decisiones de diseño técnico
- **YOLOv8n**: modelo ligero y rápido para ejecución en tiempo real.
- **Kivy**: UI multiplataforma con soporte para Android.
- **OpenCV**: captura de video confiable y compatible con Kivy.
- **Edge AI**: procesamiento local sin conexión, mayor privacidad.

## Estructura de directorios
```
.
├── assets/               # Audios de alerta
├── models/               # Pesos del modelo YOLO
├── src/                  # Código fuente
│   ├── main.py
│   ├── camera_module.py
│   ├── detector.py
│   ├── alert_engine.py
│   └── models.py
├── tests/                # Pruebas unitarias y de propiedades
├── buildozer.spec        # Configuración de Buildozer
├── README.md             # Documentación general
└── ARQUITECTURA.md       # Este documento
```
