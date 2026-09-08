"""
Модуль синтаксичного аналізу абстрактних синтаксичних дерев (AST).
Зіставляє модифіковані рядки дифу з конкретними функціями та методами бізнес-логіки.
"""

import ast
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TargetFunction:
    """
    Опис локалізованої функції або методу бізнес-логіки, що зазнали змін.
    """
    file_path: str
    name: str
    qualname: str
    start_line: int
    end_line: int
    changed_lines: list[int] = field(default_factory=list)

    @property
    def identifier(self) -> str:
        """Унікальний ідентифікатор цілі для конфігурації мутатора."""
        return f"{self.file_path}::{self.qualname}"


class AstFunctionVisitor(ast.NodeVisitor):
    """
    Відвідувач синтаксичного дерева AST для знаходження меж функцій та їхньої кваліфікації.
    """

    def __init__(self, file_path: str, changed_lines: set[int]):
        self.file_path = file_path
        self.changed_lines = changed_lines
        self.scope_stack: list[str] = []
        self.target_functions: list[TargetFunction] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        """Обробка класу зі збереженням ієрархії областей видимості."""
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def _inspect_function(self, node):
        """Перевіряє перетин меж функції із номерами змінених рядків."""
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        # Знаходимо всі змінені рядки, що належать до тіла цієї функції
        intersected = sorted([
            line for line in self.changed_lines
            if start_line <= line <= end_line
        ])

        if len(intersected) > 0:
            if len(self.scope_stack) > 0:
                qualname = ".".join(self.scope_stack) + "." + node.name
            else:
                qualname = node.name

            target = TargetFunction(
                file_path=self.file_path,
                name=node.name,
                qualname=qualname,
                start_line=start_line,
                end_line=end_line,
                changed_lines=intersected
            )
            self.target_functions.append(target)

        # Продовжуємо обхід для виявлення можливих внутрішніх функцій
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._inspect_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._inspect_function(node)


class AstFunctionLocator:
    """
    Аналізатор структури файлу для виявлення модифікованих функцій бізнес-логіки.
    """

    def locate_in_file(self, file_path: str, source_code: str, changed_lines: set[int]) -> list[TargetFunction]:
        """
        Парсить сирцевий текст файлу та повертає список змінених функцій.
        """
        if len(changed_lines) == 0:
            return []

        try:
            tree = ast.parse(source_code, filename=file_path)
        except SyntaxError:
            # У разі синтаксичної помилки код не підлягає аналізу
            return []

        visitor = AstFunctionVisitor(file_path, changed_lines)
        visitor.visit(tree)
        return visitor.target_functions

    def locate_all(self, files_changed_lines: dict[str, set[int]], file_reader=None) -> list[TargetFunction]:
        """
        Локалізує всі змінені функції по набору модифікованих файлів.
        """
        all_targets: list[TargetFunction] = []

        for file_path, lines_set in files_changed_lines.items():
            if file_reader is not None:
                source = file_reader(file_path)
            else:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()
                except OSError:
                    continue

            targets = self.locate_in_file(file_path, source, lines_set)
            all_targets.extend(targets)

        return all_targets
