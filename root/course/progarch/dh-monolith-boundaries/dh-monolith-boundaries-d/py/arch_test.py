# arch_test.py — виконуваний тест графа (import-linter-стиль)
ALLOWED = {
    "automations": {"twin", "ids", "identity"},
    "billing":     {"ids", "identity"},             # НЕ control!
    "telemetry":   {"ids", "identity"},             # control знають лише через подію
}
def test_no_forbidden_import():
    for module, deps in actual_imports().items():
        leaked = deps - ALLOWED[module]
        assert not leaked, f"{module} проліз повз двері: {leaked}"
