import os
import sys
import time
import requests
from typing import Generator, Iterable

CHUNK_SIZE = 64 * 1024  # Фіксований буфер 64 КБ


def generate_large_stream(total_bytes: int, chunk_size: int = CHUNK_SIZE) -> Generator[bytes, None, None]:
    """Генератор, що віддає масивний потік даних порціями без завантаження всього об'єму в RAM."""
    sent = 0
    pattern = b"0123456789ABCDEF" * (chunk_size // 16)
    while sent < total_bytes:
        to_send = min(chunk_size, total_bytes - sent)
        if to_send < chunk_size:
            yield pattern[:to_send]
        else:
            yield pattern
        sent += to_send


def streaming_download_and_transform(src_url: str, dst_url: str) -> int:
    """Потоковий тунель: викачує дані з джерела та відразу транслює на інший сервер."""
    total_piped = 0

    # stream=True запобігає завантаженню response.content у пам'ять
    with requests.get(src_url, stream=True, timeout=30.0) as resp:
        resp.raise_for_status()

        def stream_consumer() -> Generator[bytes, None, None]:
            nonlocal total_piped
            # iter_content зчитує сирі байти з внутрішнього сокета urllib3
            for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:
                    continue
                total_piped += len(chunk)
                # Передаємо оброблений фрагмент безпосередньо у вихідний потік
                yield chunk

        # Передавання генератора в data активує Transfer-Encoding: chunked у запиті
        upload_resp = requests.post(dst_url, data=stream_consumer(), timeout=60.0)
        upload_resp.raise_for_status()

    return total_piped
