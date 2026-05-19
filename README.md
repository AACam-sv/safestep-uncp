# safestep-uncp
## SafeStep UNCP

SafeStep UNCP es una aplicación móvil de Edge AI para asistir a estudiantes con discapacidad visual en la UNCP. La app captura video en tiempo real, detecta obstáculos (personas, sillas y mochilas) con YOLOv8n, y emite alertas de audio direccionales para guiar al usuario de manera segura.

### Requisitos
- Python 3.10+
- Cámara disponible
- Dependencias listadas en `requirements.txt`

### Instalación
```bash
python -m pip install -r requirements.txt
```

### Descarga del modelo
El archivo `models/yolov8n.pt` no se versiona. Descárgalo y colócalo en `models/`:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
mv yolov8n.pt models/yolov8n.pt
```

### Ejecución local
```bash
python -m src.main
```

### Compilación del APK (Buildozer)
1. Instala Buildozer:
   ```bash
   python -m pip install buildozer
   ```
2. Genera el APK:
   ```bash
   buildozer android debug
   ```

El archivo `buildozer.spec` ya incluye permisos de cámara e internet, y dependencias necesarias.

---

## Re-entrenamiento del modelo con Azure Machine Learning (AML)

### 1. Configurar un workspace en AML
Puedes crear el workspace desde el portal de Azure o con la CLI de Azure:
```bash
az ml workspace create -n safestep-uncp-ml -g <tu-grupo> -l <tu-region>
```

### 2. Formato del dataset (YOLO)
Estructura recomendada:
```
dataset/
  images/
    train/
    val/
  labels/
    train/
    val/
```
Cada imagen tiene un `.txt` correspondiente con anotaciones en formato:
```
<class_id> <x_center> <y_center> <width> <height>
```
Los valores están normalizados entre 0 y 1.

### 3. Entrenamiento con Ultralytics
```bash
yolo train model=yolov8n.pt data=dataset.yaml epochs=50 imgsz=640
```

### 4. Exportar y reemplazar el modelo
```bash
yolo export model=runs/detect/train/weights/best.pt format=torchscript
```

Reemplaza el archivo en `models/yolov8n.pt` con el nuevo modelo exportado.
