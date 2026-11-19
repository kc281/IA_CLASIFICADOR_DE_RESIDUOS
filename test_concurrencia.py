import os
import time
import requests
import concurrent.futures

# URL de tu API local
URL = "http://localhost:8000/predict"
TEST_DATA = "test_data"

# Recolectamos 20 imágenes aleatorias de tu dataset para la prueba
imagenes_prueba = []
for clase in os.listdir(TEST_DATA):
    carpeta = os.path.join(TEST_DATA, clase)
    if os.path.isdir(carpeta):
        for img in os.listdir(carpeta)[:10]: # Tomamos 4 de cada clase (20 total)
            imagenes_prueba.append(os.path.join(carpeta, img))

# Función que envía una imagen
def enviar_peticion(ruta_img):
    try:
        with open(ruta_img, "rb") as f:
            start = time.perf_counter()
            files = {"file": (os.path.basename(ruta_img), f, "image/jpeg")}
            respuesta = requests.post(URL, files=files, timeout=30)
            fin = time.perf_counter()
            
            tiempo = fin - start
            return respuesta.status_code, tiempo
    except Exception as e:
        return str(e), 0.0

def ejecutar_prueba(cantidad_imagenes):
    print(f"\n🚀 Iniciando ráfaga de {cantidad_imagenes} imágenes simultáneas...")
    
    # Tomamos solo la cantidad solicitada
    lote = imagenes_prueba[:cantidad_imagenes]
    
    start_total = time.perf_counter()
    
    # Usamos ThreadPoolExecutor para enviar todas las peticiones AL MISMO TIEMPO
    with concurrent.futures.ThreadPoolExecutor(max_workers=cantidad_imagenes) as executor:
        resultados = list(executor.map(enviar_peticion, lote))
        
    end_total = time.perf_counter()
    
    # Analizamos los resultados
    exitos = sum(1 for r in resultados if r[0] == 200)
    fallos = len(lote) - exitos
    tiempos = [r[1] for r in resultados if r[0] == 200]
    
    print(f"✅ Peticiones exitosas (200 OK): {exitos}")
    print(f"❌ Peticiones fallidas: {fallos}")
    if tiempos:
        print(f"⏱️ Tiempo máximo de espera para un usuario: {max(tiempos):.3f} segundos")
        print(f"⏱️ Tiempo promedio por petición: {(sum(tiempos)/len(tiempos)):.3f} segundos")
    print(f"⏳ Tiempo total del lote: {end_total - start_total:.3f} segundos")

if __name__ == "__main__":
    # Asegúrate de tener el servidor de uvicorn corriendo en otra ventana
    ejecutar_prueba(5)   # Ráfaga suave
    ejecutar_prueba(20)  # Ráfaga fuerte
    ejecutar_prueba(50)  # Estrés extremo (si el computador aguanta)