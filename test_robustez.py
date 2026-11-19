import os
import numpy as np
from PIL import Image, ImageEnhance
from sklearn.metrics import f1_score
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from backend.app.model_loader import predict

CLASES = ["biological", "cardboard", "metal", "paper", "plastic"]
TEST_DATA = "test_data"

def evaluar_transformacion(nombre, transformacion):
    y_true, y_pred = [], []
    for idx, clase in enumerate(CLASES):
        carpeta = os.path.join(TEST_DATA, clase)
        for img_name in sorted(os.listdir(carpeta))[:15]:
            img = Image.open(os.path.join(carpeta, img_name)).convert("RGB")
            
            # Aplicamos la transformación adversa
            img_modificada = transformacion(img)
            
            res = predict(img_modificada)
            y_true.append(idx)
            y_pred.append(CLASES.index(res["clase"]))
    
    f1 = f1_score(y_true, y_pred, average='macro')
    print(f"  - {nombre.ljust(20)}: F1-Macro = {f1:.4f}")

# Definimos las transformaciones
def oscurecer(img): return ImageEnhance.Brightness(img).enhance(0.4)
def girar(img): return img.rotate(90)
def pixelear(img): return img.resize((32, 32)).resize((224, 224)) # Simula cámara mala

print("Evaluando Robustez del Modelo...")
evaluar_transformacion("Original", lambda x: x)
evaluar_transformacion("Oscura (Brillo 40%)", oscurecer)
evaluar_transformacion("Girada 90 grados", girar)
evaluar_transformacion("Baja Resolución", pixelear)