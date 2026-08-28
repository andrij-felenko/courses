import hashlib
import html.parser
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional, Tuple


def normalize_package_name(name: str) -> str:
    """Приведення імені проекту до канонічного вигляду за PEP 503."""
    return re.sub(r"[-_.]+", "-", name).lower()


class SimpleIndexParser(html.parser.HTMLParser):
    """Парсер HTML-сторінки репозиторію PEP 503 на базі скінченного автомата."""

    def __init__(self):
        super().__init__()
        self.links: List[Tuple[str, str, Optional[str]]] = []
        self._current_href: Optional[str] = None
        self._current_text: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        if tag == "a":
            attrs_dict = dict(attrs)
            self._current_href = attrs_dict.get("href")
            self._current_text = []

    def handle_data(self, data: str):
        if self._current_href is not None:
            self._current_text.append(data)

    def handle_endtag(self, tag: str):
        if tag == "a" and self._current_href is not None:
            filename = "".join(self._current_text).strip()
            url_parts = urllib.parse.urldefrag(self._current_href)
            base_url = url_parts.url
            expected_hash = None
            if url_parts.fragment.startswith("sha256="):
                expected_hash = url_parts.fragment[len("sha256="):]
            self.links.append((filename, base_url, expected_hash))
            self._current_href = None
            self._current_text = []


def fetch_and_verify_package(
    index_url: str,
    package_name: str,
    target_filename: str,
    output_path: str
) -> bool:
    """Завантаження та потокова перевірка хешу пакета з захистом від OOM."""
    norm_name = normalize_package_name(package_name)
    project_url = f"{index_url.rstrip('/')}/{norm_name}/"

    req = urllib.request.Request(
        project_url,
        headers={"User-Agent": "MinimalPipClient/1.0", "Accept": "text/html"}
    )

    with urllib.request.urlopen(req) as resp:
        html_content = resp.read().decode("utf-8")

    parser = SimpleIndexParser()
    parser.feed(html_content)

    matched = [
        (url, h) for fn, url, h in parser.links if fn == target_filename
    ]
    if not matched:
        raise FileNotFoundError(f"Файл {target_filename} не знайдено в індексі {project_url}")

    rel_url, expected_sha256 = matched[0]
    download_url = urllib.parse.urljoin(project_url, rel_url)

    # Потокове завантаження блоками по 64 КБ
    hasher = hashlib.sha256()
    with urllib.request.urlopen(download_url) as resp, open(output_path, "wb") as out_file:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
            out_file.write(chunk)

    computed_sha256 = hasher.hexdigest()
    if expected_sha256 and computed_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"Помилка хешу! Очікувано: {expected_sha256}, отримано: {computed_sha256}"
        )

    return True
