import time
import threading
from camera_inspection_sdk import CameraSystem, CameraDevice, CameraError

def watchdog_loop(camera_holder: dict):
    while True:
        time.sleep(1.0)
        camera = camera_holder.get("cam")
        if camera and not camera.is_connected():
            print("Втрата пакета серцебиття камери! Запуск переініціалізації...")
            try:
                camera.close()
            except Exception:
                pass
            camera_holder["cam"] = None

            # Цикл автоматичного підключення Hot-plug
            while True:
                time.sleep(2.0)
                devices = CameraSystem.enumerate_devices()
                if devices:
                    try:
                        new_cam = CameraSystem.open_device(devices[0].id)
                        new_cam.set_parameter("ExposureTimeUs", 2500.0)
                        new_cam.start_acquisition()
                        camera_holder["cam"] = new_cam
                        print("Камеру успішно відновлено на шині.")
                        break
                    except CameraError:
                        continue
