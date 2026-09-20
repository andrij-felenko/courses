"""
ast_scanner.py
Модуль синтаксичного розбору вихідного коду на основі ast.
Містить відвідувачів AST для вилучення сигнатур функцій утиліт та
фіксації викликів функцій у клієнтських модулях.
"""

import ast
from pathlib import Path
from typing import List, Dict, Set, Optional
from models import FunctionSignature, CallReference


def _ast_to_str(node: Optional[ast.AST]) -> Optional[str]:
    """Перетворює вузол аннотації AST у текстове представлення типу."""
    if node is None:
        return None
    if hasattr(ast, "unparse"):
        return ast.unparse(node)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_ast_to_str(node.value)}.{node.attr}"
    if isinstance(node, ast.Constant):
        return str(node.value)
    return str(node)


class UtilityVisitor(ast.NodeVisitor):
    """Синтаксичний відвідувач для обходу модулів утиліт і збору сигнатур функцій."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.signatures: List[FunctionSignature] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)

    def _process_function(self, node: ast.AST) -> None:
        func_name = getattr(node, "name", "")
        if func_name.startswith("__") and func_name.endswith("__"):
            return

        params = [arg.arg for arg in node.args.args]
        type_annotations = {}
        for arg in node.args.args:
            if arg.annotation:
                ann_str = _ast_to_str(arg.annotation)
                if ann_str:
                    type_annotations[arg.arg] = ann_str

        return_annotation = _ast_to_str(node.returns) if node.returns else None

        sig = FunctionSignature(
            name=func_name,
            file_path=self.file_path,
            line_number=node.lineno,
            parameters=params,
            type_annotations=type_annotations,
            return_annotation=return_annotation,
        )
        self.signatures.append(sig)


class CallSiteVisitor(ast.NodeVisitor):
    """Синтаксичний відвідувач для аналізу імпортів і точок викликів у клієнтських модулях."""

    def __init__(self, consumer_module: str, target_functions: Set[str]):
        self.consumer_module = consumer_module
        self.target_functions = target_functions
        self.calls: List[CallReference] = []
        self.imported_names: Dict[str, str] = {}
        self.imported_modules: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            mod_name = alias.name
            local_alias = alias.asname or mod_name
            self.imported_modules.add(local_alias)
            self.imported_modules.add(mod_name.split(".")[-1])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            imported_symbol = alias.name
            local_alias = alias.asname or imported_symbol
            if imported_symbol in self.target_functions:
                self.imported_names[local_alias] = imported_symbol
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func_name = None
        import_style = "unknown"

        if isinstance(node.func, ast.Name):
            called_id = node.func.id
            if called_id in self.imported_names:
                func_name = self.imported_names[called_id]
                import_style = "from_import"
            elif called_id in self.target_functions:
                func_name = called_id
                import_style = "direct_call"

        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module_var = node.func.value.id
                method_name = node.func.attr
                if method_name in self.target_functions:
                    func_name = method_name
                    import_style = f"qualified ({module_var})"

        if func_name and func_name in self.target_functions:
            self.calls.append(
                CallReference(
                    consumer_module=self.consumer_module,
                    line_number=node.lineno,
                    import_style=import_style,
                    function_name=func_name,
                )
            )

        self.generic_visit(node)


class AstScanner:
    """Координатор статичного синтаксичного аналізу кодової бази."""

    def parse_code(self, source_code: str, filename: str = "<unknown>") -> ast.AST:
        """Перетворює рядок коду Python на синтаксичне дерево AST."""
        return ast.parse(source_code, filename=filename)

    def scan_utility_sources(self, sources: Dict[str, str]) -> List[FunctionSignature]:
        """Сканує вхідні джерела коду утиліт у формі {шлях: вміст}."""
        signatures: List[FunctionSignature] = []
        for file_path, content in sources.items():
            tree = self.parse_code(content, filename=file_path)
            visitor = UtilityVisitor(file_path=file_path)
            visitor.visit(tree)
            signatures.extend(visitor.signatures)
        return signatures

    def scan_utility_files(self, file_paths: List[str]) -> List[FunctionSignature]:
        """Зчитує файли утиліт із диска та вилучає їхні сигнатури."""
        sources = {}
        for p in file_paths:
            path_obj = Path(p)
            if path_obj.exists() and path_obj.is_file():
                sources[str(path_obj)] = path_obj.read_text(encoding="utf-8")
        return self.scan_utility_sources(sources)

    def scan_client_sources(
        self, sources: Dict[str, str], target_functions: Set[str]
    ) -> List[CallReference]:
        """Сканує клієнтські джерела коду у формі {шлях: вміст} на предмет викликів утиліт."""
        all_calls: List[CallReference] = []
        for file_path, content in sources.items():
            tree = self.parse_code(content, filename=file_path)
            visitor = CallSiteVisitor(
                consumer_module=file_path, target_functions=target_functions
            )
            visitor.visit(tree)
            all_calls.extend(visitor.calls)
        return all_calls

    def scan_client_files(
        self, file_paths: List[str], target_functions: Set[str]
    ) -> List[CallReference]:
        """Зчитує клієнтські файли з диска та аналізує точки викликів утиліт."""
        sources = {}
        for p in file_paths:
            path_obj = Path(p)
            if path_obj.exists() and path_obj.is_file():
                sources[str(path_obj)] = path_obj.read_text(encoding="utf-8")
        return self.scan_client_sources(sources, target_functions)
