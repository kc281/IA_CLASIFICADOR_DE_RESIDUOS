import sys
import os
import time
import numpy as np
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix, f1_score, recall_score

# Arreglo de rutas para encontrar el backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.app.model_loader import predict

CLASES = ["biological", "cardboard", "metal", "paper", "plastic"]
TEST_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data'))

y_true = []
y_pred = []
latencias = []

print("⏳ Iniciando evaluación de las 75 imágenes...\n")

for idx, clase in enumerate(CLASES):
    carpeta = os.path.join(TEST_DATA, clase)
    imagenes = sorted(os.listdir(carpeta))[:15]
    
    for img_name in imagenes:
        img_path = os.path.join(carpeta, img_name)
        img = Image.open(img_path)
        
        t0 = time.perf_counter()
        resultado = predict(img)
        t1 = time.perf_counter()
        
        y_true.append(idx)
        clase_predicha = resultado["clase"]
        y_pred.append(CLASES.index(clase_predicha))
        latencias.append(t1 - t0)

# ─── Cálculo de métricas ───
print("="*50)
print("📊 RESULTADOS DE LA EVALUACIÓN")
print("="*50)

# 1. F1-Macro
f1_macro = f1_score(y_true, y_pred, average='macro')
print(f"\n⭐ F1-Macro General: {f1_macro:.4f}")

# 2. Recall por clase
recalls = recall_score(y_true, y_pred, average=None)
print("\n🎯 Recall por clase (Sensibilidad):")
for i, clase in enumerate(CLASES):
    print(f"  - {clase.ljust(12)}: {recalls[i]:.4f}")

# 3. Reporte completo
print("\n📋 Reporte de Clasificación Detallado:")
print(classification_report(y_true, y_pred, target_names=CLASES, zero_division=0))

# 4. Matriz de Confusión
print("🔢 Matriz de Confusión (Filas = Real, Columnas = Predicho):")
matriz = confusion_matrix(y_true, y_pred)
print(f"{'':>12} " + " ".join([c[:4].center(5) for c in CLASES]))
for i, clase in enumerate(CLASES):
    fila = " ".join([str(val).center(5) for val in matriz[i]])
    print(f"{clase.ljust(12)} {fila}")

# 5. Latencia
p95 = np.percentile(latencias, 95)
print(f"\n⏱️ Latencia p95: {p95*1000:.1f} ms (Criterio de aprobación: < 2000 ms)")