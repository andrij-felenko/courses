import os
import requests
from typing import Generator

CHUNK_SIZE = 64 * 1024  # 64 кілобайти


def download_stream(url: str, output_path: str) -> int:
    """Потокове завантаження: викачує файл порціями по 64 КБ без накопичення в RAM."""
    total_bytes = 0
    # stream=True утримує сокет відкритим і не вичитує response.content
    with requests.get(url, stream=True, timeout=30.0) as response:
        response.raise_for_status()
        with open(output_path, "wb") as f:
            # iter_content зчитує байти безпосередньо з сокета ядра
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
                    total_bytes += len(chunk)
    return total_bytes


def file_chunk_generator(file_path: str, chunk_size: int = CHUNK_SIZE) -> Generator[bytes, None, None]:
    """Генератор, що зчитує масивний локальний файл фіксованими порціями."""
    with open(file_path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data


def upload_stream(url: str, file_path: str) -> None:
    """Потокове вивантаження: передавання генератора в data активує chunked encoding."""
    stream = file_chunk_generator(file_path)
    response = requests.post(url, data=stream, timeout=60.0)
    response.raise_for_status()
