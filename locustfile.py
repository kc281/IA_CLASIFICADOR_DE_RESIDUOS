from locust import HttpUser, task, between
import io
from PIL import Image

def get_test_image():
    img = Image.new("RGB", (224, 224), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

class ClasificadorUser(HttpUser):
   
    wait_time = between(1, 3)

    @task
    def predecir_imagen(self):
        files = {'file': ('test.jpg', get_test_image(), 'image/jpeg')}
        self.client.post("/predict", files=files)