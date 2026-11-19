import sys
import os
import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Arreglo de rutas para que encuentre la carpeta backend y app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.app.main import app

client = TestClient(app)

CLASES = ["biological", "cardboard", "metal", "paper", "plastic"]
TEST_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_data'))

# ---------- A1: Swagger disponible ----------
def test_A1_docs_available():
    r = client.get("/docs")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]

# ---------- Extra: Health y Model Info (de tu script original) ----------
def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_model_info():
    r = client.get("/model-info")
    assert r.status_code == 200

# ---------- A2: 75 imágenes reales devuelven 200 ----------
@pytest.mark.parametrize("clase", CLASES)
def test_A2_predict_valid_image(clase):
    carpeta = os.path.join(TEST_DATA, clase)
    assert os.path.exists(carpeta), f"No existe la carpeta {carpeta}"
    
    imagenes = sorted(os.listdir(carpeta))[:15]
    assert len(imagenes) == 15, f"Faltan imágenes en {clase}"

    for img in imagenes:
        with open(os.path.join(carpeta, img), "rb") as f:
            r = client.post(
                "/predict",
                files={"file": (img, f, "image/jpeg")}
            )
        assert r.status_code == 200, f"Falló {clase}/{img}"
        body = r.json()
        assert "clase" in body
        assert body["clase"] in CLASES
        assert 0.0 <= body["confianza"] <= 1.0

# ---------- A3: Request sin archivo → 422 ----------
def test_A3_no_file():
    r = client.post("/predict")
    assert r.status_code == 422

# ---------- A4: CORS acepta el frontend ----------
def test_A4_cors():
    r = client.options(
        "/predict",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r.status_code in (200, 204)
    assert "access-control-allow-origin" in {k.lower() for k in r.headers}