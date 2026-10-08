import sys
from camera_inspection_sdk import CameraSystem, CameraError

def main():
    # Ініціалізація системних ресурсів SDK
    CameraSystem.initialize()
    
    try:
        # Сканування шин USB 3.0 та GigE Vision
        devices = CameraSystem.enumerate_devices()
        if not devices:
            print("Інспекційні камери не виявлені.")
            return

        # Відкриття сесії з першим пристроєм зі списку
        camera = CameraSystem.open_device(devices[0].id)
        print(f"Встановлено з'єднання з: {camera.model_name}")

        # Налаштування розміру пакету транспортного рівня
        camera.set_transport_parameter("PacketSize", 9000)

        # Безпечне закриття каналу зв'язку
        camera.close()
    except CameraError as err:
        print(f"Збій виконання SDK: {err}")
    finally:
        CameraSystem.shutdown()

if __name__ == "__main__":
    main()
