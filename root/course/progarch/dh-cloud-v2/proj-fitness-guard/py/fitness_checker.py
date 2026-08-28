# fitness_checker.py — Ідіоматичний Python-еквівалент аналізатора AST для Python/C++ коду
import os
import re
import sys
from pathlib import Path
from typing import List, NamedTuple

class Violation(NamedTuple):
    source_file: str
    line_number: int
    included_header: str
    rule_name: str

class PythonArchitectureGuard:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.rules = []

    def add_rule(self, source_pattern: str, forbidden_substring: str):
        self.rules.append((source_pattern, forbidden_substring))

    def inspect(self) -> List[Violation]:
        violations = []
        include_regex = re.compile(r'^\s*(?:#include\s*["<]([^">]+)[">]|from\s+([\w\.]+)\s+import|import\s+([\w\.]+))')

        for file_path in self.root_dir.rglob('*'):
            if file_path.suffix not in ('.py', '.cpp', '.hpp', '.h', '.cc'):
                continue

            rel_path = file_path.relative_to(self.root_dir).as_posix()

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        match = include_regex.search(line)
                        if match:
                            target = match.group(1) or match.group(2) or match.group(3)
                            for src_pat, forbidden in self.rules:
                                if src_pat in rel_path and forbidden in target:
                                    violations.append(Violation(
                                        source_file=rel_path,
                                        line_number=line_num,
                                        included_header=target,
                                        rule_name="LAYER_VIOLATION: Strict separation v2 from v1"
                                    ))
            except Exception as e:
                print(f"Помилка читання файла {rel_path}: {e}", file=sys.stderr)

        return violations

if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    guard = PythonArchitectureGuard(root)
    guard.add_rule("src/v2/", "v1/legacy_db")
    guard.add_rule("src/v2/", "postgres_raw_client")
    
    found_violations = guard.inspect()
    if found_violations:
        print(f"❌ ВИЯВЛЕНО ЕРОЗІЮ АРХІТЕКТУРИ ({len(found_violations)} порушень):", file=sys.stderr)
        for v in found_violations:
            print(f"  • {v.source_file}:{v.line_number} -> '{v.included_header}'", file=sys.stderr)
        sys.exit(1)
    
    print("✅ [FITNESS GUARD] Усі архітектурні межі чисто дотримано.")
    sys.exit(0)
