import numpy as np
from camera_inspection_sdk import CameraDevice, FrameBuffer, PixelFormat

def frame_callback(buffer: FrameBuffer):
    if buffer.is_valid():
        # Перетворення RAW8/RAW12 в масив NumPy RGB24
        raw_data = buffer.get_numpy_array()
        rgb_image = buffer.convert_to_rgb24(raw_data)

        # Накладання калібрувальної вимірювальної сітки
        buffer.apply_grid_overlay(rgb_image, step_px=50, color=(0, 255, 0))

        # Збереження зображення на диск
        buffer.save_jpeg("inspection_frame.jpg", rgb_image, quality=90)

def start_stream(camera: CameraDevice):
    # Реєстрація колбеку та запуск асинхронного потоку
    camera.register_callback(frame_callback)
    camera.start_acquisition()
