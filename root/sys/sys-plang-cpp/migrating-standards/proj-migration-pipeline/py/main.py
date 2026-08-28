#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скрипт транзакційної модернізації C++ кодової бази на основі Clang-Tidy."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


class MigrationPipeline:
    def __init__(self, build_dir: str, source_dir: str):
        self.build_dir = Path(build_dir).resolve()
        self.source_dir = Path(source_dir).resolve()
        self.compilation_db = self.build_dir / "compile_commands.json"
        self.fixes_dir = self.build_dir / "clang_tidy_fixes"

        if not self.compilation_db.exists():
            raise FileNotFoundError(
                f"Не знайдено базу компіляції: {self.compilation_db}\n"
                "Згенеруйте її командою: cmake -B <build_dir> -DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
            )

        # Черга правил: послідовність від безпечних до глибоких семантичних
        self.rules_queue = [
            ("modernize-use-nullptr", "Заміна літералів 0 та макросів NULL на nullptr"),
            ("modernize-use-override", "Додавання специфікатора override до віртуальних методів"),
            ("modernize-use-using", "Заміна конструкцій typedef на синтаксис using"),
            ("modernize-redundant-void-arg", "Видалення надлишкових параметрів void у функціях"),
            ("modernize-deprecated-headers", "Міграція застарілих C-заголовків на префіксні <c*>"),
            ("modernize-replace-auto-ptr", "Заміна забороненого std::auto_ptr на std::unique_ptr"),
            ("modernize-make-unique", "Заміна явних викликів new на std::make_unique"),
            ("modernize-make-shared", "Заміна явних викликів new на std::make_shared"),
            ("modernize-loop-convert", "Трансформація індексних та ітераторних циклів у range-based for"),
            ("modernize-use-nodiscard", "Додавання атрибута [[nodiscard]] для функцій без побічних ефектів"),
            ("modernize-use-starts-ends-with", "Заміна s.find()==0 на виклики s.starts_with (C++20)"),
        ]

    def _execute(self, cmd: list[str], cwd: Path = None) -> tuple[int, str, str]:
        """Виконує команду оболонки та повертає статус, stdout і stderr."""
        work_dir = cwd if cwd else self.source_dir
        proc = subprocess.run(
            cmd,
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return proc.returncode, proc.stdout, proc.stderr

    def get_project_sources(self) -> list[str]:
        """Отримує перелік файлів власного коду проєкту з бази компіляції."""
        with open(self.compilation_db, "r", encoding="utf-8") as f:
            data = json.load(f)

        sources = []
        for entry in data:
            fpath = Path(entry["file"]).resolve()
            # Обробляємо лише файли нашого репозиторію, виключаючи сторонні залежності
            if fpath.is_relative_to(self.source_dir):
                ignored_subdirs = ["third_party", "extern", "build", "vendor", "submodules"]
                if not any(part in fpath.parts for part in ignored_subdirs):
                    if fpath.suffix in [".cpp", ".cc", ".cxx"]:
                        sources.append(str(fpath))

        return sorted(list(set(sources)))

    def apply_clang_tidy_rule(self, rule_name: str, sources: list[str]) -> bool:
        """Виконує аналіз Clang-Tidy та експортує виправлення у тимчасовий каталог."""
        if self.fixes_dir.exists():
            shutil.rmtree(self.fixes_dir)
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

        print(f"[*] Запуск AST-аналізу для правила: {rule_name} ({len(sources)} файлів)...")

        # Використовуємо run-clang-tidy для безпечного збереження заміщень у YAML
        cmd = [
            "clang-tidy",
            f"-checks=-*,{rule_name}",
            f"--export-fixes={self.fixes_dir}/fixes.yaml",
            f"-p={self.build_dir}",
            f"-header-filter=^{self.source_dir}/.*",
        ] + sources

        # Clang-Tidy може повертати ненульовий статус, якщо знайдено зауваження
        self._execute(cmd)

        fixes_file = self.fixes_dir / "fixes.yaml"
        if not fixes_file.exists() or fixes_file.stat().st_size == 0:
            print(f"[-] Правило {rule_name} не знайшло шаблонів для заміни.")
            return False

        # Детерміноване застосування виправлень без ризику гонок запису у заголовки
        print("[*] Застосування згенерованих виправлень до кодової бази...")
        apply_cmd = ["clang-apply-replacements", str(self.fixes_dir)]
        ret, out, err = self._execute(apply_cmd)
        if ret != 0:
            print(f"[!] Помилка застосування виправлень: {err}")
            return False

        return True

    def validate_build_and_tests(self) -> bool:
        """Перевіряє успішність компіляції та виконання тестів під санітайзерами."""
        print("[*] Компіляція проєкту...")
        build_cmd = ["cmake", "--build", str(self.build_dir), "--parallel"]
        ret, stdout, stderr = self._execute(build_cmd)
        if ret != 0:
            print(f"[x] Помилка збірки після модернізації:\n{stderr}")
            return False

        print("[*] Виконання тестового набору через CTest...")
        test_cmd = [
            "ctest",
            "--test-dir", str(self.build_dir),
            "--output-on-failure",
            "--parallel", str(os.cpu_count() or 4)
        ]
        ret, stdout, stderr = self._execute(test_cmd)
        if ret != 0:
            print(f"[x] Тести провалилися:\n{stdout}\n{stderr}")
            return False

        print("[✓] Компіляція та тести пройшли без зауважень.")
        return True

    def run_pipeline(self):
        """Головний цикл виконання конвеєра модернізації."""
        sources = self.get_project_sources()
        print(f"Знайдено {len(sources)} файлів вихідного коду для перевірки.")

        for rule, desc in self.rules_queue:
            print(f"\n{'='*75}\n[ФАЗА МОДЕРНІЗАЦІЇ] Правило: {rule}\nОпис: {desc}\n{'='*75}")

            has_changes = self.apply_clang_tidy_rule(rule, sources)
            if not has_changes:
                continue

            # Перевіряємо статус робочої копії Git
            ret, status_out, _ = self._execute(["git", "status", "--porcelain"])
            if not status_out.strip():
                print(f"[-] Змін у робочому дереві Git не виявлено.")
                continue

            # Верифікація поведінки кодової бази
            if self.validate_build_and_tests():
                self._execute(["git", "add", "."])
                commit_msg = f"refactor(modernize): застосовано правило {rule}\n\n{desc}"
                self._execute(["git", "commit", "-m", commit_msg])
                print(f"[✓] Успішно зафіксовано транзакцію: {rule}")
            else:
                print(f"[!] Відкат робочого дерева через збій валідації правила: {rule}")
                self._execute(["git", "reset", "--hard", "HEAD"])
                self._execute(["git", "clean", "-fd"])
                print(f"[!] Правило {rule} потребує ручного втручання.")

        print("\n[✓] Конвеєр завершив роботу. Перегляньте історію комітів Git.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Використання: python migrate_runner.py <шлях_до_build> <шлях_до_source>")
        sys.exit(1)

    pipeline = MigrationPipeline(sys.argv[1], sys.argv[2])
    pipeline.run_pipeline()
