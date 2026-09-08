import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NormalizedChange:
    # Очищена та нормалізована подія зміни файлу в історії Git
    commit_hash: str
    author_name: str
    author_email: str
    timestamp: int
    file_path: str
    lines_added: int
    lines_deleted: int


class GitNoiseFilter:
    # Конвеєр дедуплікації авторів та відсікання синтаксичного шуму

    # Розширення та шаблони шляхів файлів, що генеруються автоматично
    IGNORED_EXACT_FILES = {
        "package-lock.json",
        "pnpm-lock.yaml",
        "Cargo.lock",
        "yarn.lock",
        "poetry.lock",
    }

    IGNORED_DIRS = (
        "vendor/",
        "node_modules/",
        "dist/",
        "build/",
        ".next/",
        "generated/",
    )

    IGNORED_EXTENSIONS = (
        ".min.js",
        ".min.css",
        ".pb.go",
        "_pb2.py",
        ".generated.ts",
    )

    # Шаблони повідомлень сервісних комітів і ботів
    IGNORED_MESSAGE_PREFIXES = (
        "bump version",
        "chore(deps):",
        "style(prettier):",
        "style(black):",
    )

    def __init__(self, mailmap_path: Path | None = None) -> None:
        self._mailmap: dict[tuple[str, str], tuple[str, str]] = {}
        if mailmap_path and mailmap_path.is_file():
            self._load_mailmap(mailmap_path)

    def _load_mailmap(self, path: Path) -> None:
        # Зчитує правила зіставляння імен та адрес із файлу .mailmap
        # Формат: Canonical Name <canonical@email> Old Name <old@email>
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Розбір адреси та імені за кутовими дужками
                if "<" not in line or ">" not in line:
                    continue
                parts = line.split(">")
                first_part = parts[0]
                canon_name = first_part.split("<")[0].strip()
                canon_email = first_part.split("<")[1].strip().lower()

                if len(parts) > 1 and "<" in parts[1]:
                    second_part = parts[1]
                    orig_name = second_part.split("<")[0].strip() or canon_name
                    orig_email = second_part.split("<")[1].strip().lower()
                else:
                    orig_name = canon_name
                    orig_email = canon_email

                self._mailmap[(orig_name, orig_email)] = (canon_name, canon_email)

    def resolve_author(self, name: str, email: str) -> tuple[str, str]:
        # Повертає канонічне ім'я та email автора з урахуванням .mailmap
        cleaned_name = name.strip()
        cleaned_email = email.strip().lower()
        key = (cleaned_name, cleaned_email)
        if key in self._mailmap:
            return self._mailmap[key]
        # Перевірка збігу лише за поштовою адресою
        for (m_name, m_email), (c_name, c_email) in self._mailmap.items():
            if m_email == cleaned_email and (not m_name or m_name == cleaned_name):
                return c_name, c_email
        return cleaned_name, cleaned_email

    def is_noise_path(self, file_path: str) -> bool:
        # Перевіряє, чи належить файл до вендорних або згенерованих артефактів
        posix_path = Path(file_path).as_posix()
        file_name = Path(file_path).name

        if file_name in self.IGNORED_EXACT_FILES:
            return True
        if any(d in posix_path for d in self.IGNORED_DIRS):
            return True
        if any(file_name.endswith(ext) for ext in self.IGNORED_EXTENSIONS):
            return True
        return False

    def is_noise_commit(self, message: str, files_changed: int, total_lines: int) -> bool:
        # Визначає, чи є коміт сервісним, або масовим реформатуванням коду
        lower_msg = message.strip().lower()
        if any(lower_msg.startswith(prefix) for prefix in self.IGNORED_MESSAGE_PREFIXES):
            return True
        # Евристика масового форматування: зачеплено понад 100 файлів із великим обсягом рядків
        if files_changed > 100 and total_lines > 5000:
            return True
        return False
