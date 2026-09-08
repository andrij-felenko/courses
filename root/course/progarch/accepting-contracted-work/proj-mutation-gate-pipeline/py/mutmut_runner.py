"""
Модуль керування та виконання мутаційного тестування.
Взаємодіє з Mutmut і pytest та містить автономний рушій цільових мутацій.
"""

import ast
import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any
from ast_locator import TargetFunction


class MutantStatus(str, Enum):
    """Статуси результату тестування мутанта."""
    KILLED = "KILLED"          # Тести підрядника провалилися (мутант знищений, тест якісний)
    SURVIVED = "SURVIVED"      # Тести успішно пройшли попри баг (мутант вижив, тест неефективний)
    TIMEOUT = "TIMEOUT"        # Мутація спричинила нескінченний цикл чи таймаут
    SUSPICIOUS = "SUSPICIOUS"  # Невизначена поведінка або помилка середовища


@dataclass
class MutantRecord:
    """Опис окремого синтетичного мутанта та наслідків його виконання."""
    id: int
    file_path: str
    function_name: str
    line_number: int
    original_code: str
    mutated_code: str
    status: MutantStatus
    description: str


class TargetedAstMutator(ast.NodeTransformer):
    """
    Трансформатор синтаксичного дерева AST для генерації контрольованих мутацій
    відповідно до стандартного набору мутаційних операторів Mutmut.
    """

    def __init__(self, target_line: int, operator_type: str):
        self.target_line = target_line
        self.operator_type = operator_type
        self.applied = False
        self.original_snippet = ""
        self.mutated_snippet = ""
        self.mutation_description = ""

    def visit_Compare(self, node: ast.Compare):
        """Мутація операторів порівняння (граничні значення)."""
        if not self.applied and node.lineno == self.target_line and len(node.ops) == 1:
            op = node.ops[0]
            if isinstance(op, ast.Gt):
                # Заміна строгої нерівності > на нестрогу >=
                node.ops = [ast.GtE()]
                self.applied = True
                self.original_snippet = ">"
                self.mutated_snippet = ">="
                self.mutation_description = "Заміна строгої нерівності '>' на нестрогу '>=' (порушення граничної умови)"
                return node
            elif isinstance(op, ast.Lt):
                # Заміна строгої нерівності < на нестрогу <=
                node.ops = [ast.LtE()]
                self.applied = True
                self.original_snippet = "<"
                self.mutated_snippet = "<="
                self.mutation_description = "Заміна строгої нерівності '<' на нестрогу '<=' (порушення граничної умови)"
                return node
            elif isinstance(op, ast.Eq):
                # Заміна рівності == на нерівність !=
                node.ops = [ast.NotEq()]
                self.applied = True
                self.original_snippet = "=="
                self.mutated_snippet = "!="
                self.mutation_description = "Інверсія оператора рівності '==' на '!='"
                return node
        return self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        """Мутація арифметичних операторів."""
        if not self.applied and node.lineno == self.target_line:
            if isinstance(node.op, ast.Add):
                node.op = ast.Sub()
                self.applied = True
                self.original_snippet = "+"
                self.mutated_snippet = "-"
                self.mutation_description = "Заміна оператора додавання '+' на віднімання '-'"
                return node
            elif isinstance(node.op, ast.Sub):
                node.op = ast.Add()
                self.applied = True
                self.original_snippet = "-"
                self.mutated_snippet = "+"
                self.mutation_description = "Заміна оператора віднімання '-' на додавання '+'"
                return node
            elif isinstance(node.op, ast.Mult):
                node.op = ast.FloorDiv()
                self.applied = True
                self.original_snippet = "*"
                self.mutated_snippet = "//"
                self.mutation_description = "Заміна оператора множення '*' на цілочисельне ділення '//'"
                return node
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        """Мутація констант (булеві значення та числові коефіцієнти)."""
        if not self.applied and node.lineno == self.target_line:
            if isinstance(node.value, bool):
                node.value = not node.value
                self.applied = True
                self.original_snippet = str(not node.value)
                self.mutated_snippet = str(node.value)
                self.mutation_description = f"Інверсія булевої константи {self.original_snippet} на {self.mutated_snippet}"
                return node
            elif isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                old_val = node.value
                if node.value == 0:
                    node.value = 1
                elif node.value == 1:
                    node.value = 0
                else:
                    node.value = round(node.value * 1.5, 4)
                self.applied = True
                self.original_snippet = str(old_val)
                self.mutated_snippet = str(node.value)
                self.mutation_description = f"Модифікація числової константи {self.original_snippet} -> {self.mutated_snippet}"
                return node
        return self.generic_visit(node)


class MutmutRunner:
    """
    Раннер мутаційного тестування.
    Забезпечує інтеграцію з CLI-командою Mutmut та виконання цільових мутацій.
    """

    def build_mutmut_cli_command(
        self,
        targets: list[TargetFunction],
        tests_dir: str = "tests",
        runner: str = "pytest -q"
    ) -> list[str]:
        """
        Формує команду запуску Mutmut CLI для переданих цілей.
        """
        files = sorted(list(set(t.file_path for t in targets)))
        paths_arg = ",".join(files)
        return [
            "mutmut",
            "run",
            f"--paths-to-mutate={paths_arg}",
            f"--tests-dir={tests_dir}",
            f"--runner={runner}"
        ]

    def test_single_mutation(
        self,
        source_code: str,
        target_line: int,
        test_callable: Callable[[dict[str, Any]], bool],
        file_path: str,
        func_name: str,
        mutant_id: int
    ) -> Optional[MutantRecord]:
        """
        Застосовує одну синтетичну мутацію на вказаному рядку та перевіряє реакцію тестів.
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return None

        mutator = TargetedAstMutator(target_line, "all")
        mutated_tree = mutator.visit(copy.deepcopy(tree))
        ast.fix_missing_locations(mutated_tree)

        if not mutator.applied:
            return None

        # Компілюємо мутований код у локальний простір імен
        compiled_code = compile(mutated_tree, filename=file_path, mode="exec")
        mutated_namespace: dict[str, Any] = {}
        try:
            exec(compiled_code, mutated_namespace)
        except Exception:
            return MutantRecord(
                id=mutant_id,
                file_path=file_path,
                function_name=func_name,
                line_number=target_line,
                original_code=mutator.original_snippet,
                mutated_code=mutator.mutated_snippet,
                status=MutantStatus.KILLED,
                description=mutator.mutation_description + " (виклик викликав виняток під час ініціалізації)"
            )

        # Запускаємо тестовий набір проти мутованого простору імен
        try:
            test_passed = test_callable(mutated_namespace)
            if test_passed:
                # Тести пройшли успішно, не помітивши внесеного дефекту -> мутант вижив!
                status = MutantStatus.SURVIVED
            else:
                # Тести помітили баг і впали -> мутант знищений!
                status = MutantStatus.KILLED
        except AssertionError:
            # Твердження assert впало -> мутант знищений якісним тестом
            status = MutantStatus.KILLED
        except Exception:
            # Інший збій виконання під час тесту -> мутант знищений
            status = MutantStatus.KILLED

        return MutantRecord(
            id=mutant_id,
            file_path=file_path,
            function_name=func_name,
            line_number=target_line,
            original_code=mutator.original_snippet,
            mutated_code=mutator.mutated_snippet,
            status=status,
            description=mutator.mutation_description
        )

    def run_targeted_suite(
        self,
        target_functions: list[TargetFunction],
        source_code_provider: Callable[[str], str],
        test_executor: Callable[[str, dict[str, Any]], bool]
    ) -> list[MutantRecord]:
        """
        Проганяє мутаційний аналіз для всіх виявлених цілей бізнес-логіки.
        """
        records: list[MutantRecord] = []
        mutant_counter = 1

        for target in target_functions:
            source = source_code_provider(target.file_path)
            for line in target.changed_lines:
                record = self.test_single_mutation(
                    source_code=source,
                    target_line=line,
                    test_callable=lambda ns, p=target.file_path: test_executor(p, ns),
                    file_path=target.file_path,
                    func_name=target.qualname,
                    mutant_id=mutant_counter
                )
                if record is not None:
                    records.append(record)
                    mutant_counter += 1

        return records
