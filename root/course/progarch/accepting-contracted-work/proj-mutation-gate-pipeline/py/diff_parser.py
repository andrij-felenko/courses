"""
Модуль синтаксичного аналізу виводу git diff.
Виявляє модифіковані файли та номери змінених рядків у межах пул-реквесту.
"""

import subprocess
import re
from typing import Optional


class DiffParser:
    """
    Парсер диференційного зрізу git diff для виділення змінених рядків коду.
    """

    def __init__(self, target_extensions: Optional[list[str]] = None):
        """
        Ініціалізує парсер із фільтром розширень файлів.
        За замовчуванням обробляються лише файли з розширенням .py.
        """
        if target_extensions is None:
            self.target_extensions = [".py"]
        else:
            self.target_extensions = target_extensions

    def is_target_file(self, file_path: str) -> bool:
        """
        Перевіряє, чи належить файл до цільових для аналізу.
        Виключає тестові каталоги, службові файли та файли з нецільовими розширеннями.
        """
        if not any(file_path.endswith(ext) for ext in self.target_extensions):
            return False
        # Ігноруємо каталоги тестів та службові папки
        normalized = file_path.replace("//", "/")
        excluded_parts = ["tests/", "test_", "/test/", ".venv/", "venv/", ".git/"]
        for part in excluded_parts:
            if part in normalized or normalized.startswith("tests/"):
                return False
        return True

    def parse_unified_diff(self, diff_text: str) -> dict[str, set[int]]:
        """
        Парсить уніфікований текст git diff і повертає словник:
        шлях до файлу -> множина номерів змінених/доданих рядків у новій версії.
        """
        changed_files_lines: dict[str, set[int]] = {}
        current_file: Optional[str] = None
        current_line_num: int = 0
        in_hunk: bool = False

        # Розбиваємо текст дифу на рядки
        lines = diff_text.splitlines()

        # Регулярний вираз для заголовка чанка: @@ -старий,довжина +новий,довжина @@
        # Символ [+] використовується для прямого пошуку знака плюса без зворотних слешів
        hunk_pattern = re.compile("^@@ -[0-9]+(,[0-9]+)? [+]([0-9]+)(,[0-9]+)? @@")

        for line in lines:
            if line.startswith("diff --git "):
                in_hunk = False
                current_file = None
                continue

            if line.startswith("+++ b/"):
                raw_path = line[6:].strip()
                if self.is_target_file(raw_path):
                    current_file = raw_path
                    if current_file not in changed_files_lines:
                        changed_files_lines[current_file] = set()
                else:
                    current_file = None
                in_hunk = False
                continue

            if current_file is None:
                continue

            match = hunk_pattern.match(line)
            if match:
                in_hunk = True
                # Початковий номер рядка у новому файлі (друга числова група)
                current_line_num = int(match.group(2))
                continue

            if in_hunk:
                if line.startswith("+") and not line.startswith("+++"):
                    # Рядок додано або змінено в пул-реквесті
                    changed_files_lines[current_file].add(current_line_num)
                    current_line_num += 1
                elif line.startswith("-"):
                    # Рядок видалено зі старої версії
                    pass
                else:
                    # Контекстний незмінений рядок
                    current_line_num += 1

        # Повертаємо лише ті файли, де є реальні зміни рядків
        return {f: lines_set for f, lines_set in changed_files_lines.items() if len(lines_set) > 0}

    def fetch_diff_from_git(self, base_branch: str = "main", head_branch: str = "HEAD") -> str:
        """
        Отримує git diff між базовою гілкою та гілкою PR через виклик утиліти git.
        """
        cmd = ["git", "diff", "--unified=0", f"{base_branch}...{head_branch}"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8"
            )
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
