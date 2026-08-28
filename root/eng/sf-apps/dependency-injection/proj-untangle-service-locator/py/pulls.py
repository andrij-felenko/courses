# pulls.py — інвентаризація смиків: хто з локатора що бере
import ast, os, sys, collections

def pulls_in(path):
    """(клас, метод, ключ, рядок) для кожного Locator.get(...) у файлі."""
    tree = ast.parse(open(path, encoding='utf-8').read(), path)
    found = []
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        for fn in [n for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)]:
            for call in [n for n in ast.walk(fn) if isinstance(n, ast.Call)]:
                f = call.func
                if isinstance(f, ast.Attribute) and f.attr == 'get' \
                   and isinstance(f.value, ast.Name) and f.value.id == 'Locator':
                    arg = call.args[0] if call.args else None
                    key = arg.value if isinstance(arg, ast.Constant) else '<ОБЧИСЛЕНИЙ>'
                    found.append((cls.name, fn.name, key, call.lineno))
    return found

def scan(root):
    out = collections.defaultdict(list)
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if fname.endswith('.py'):
                p = os.path.join(dirpath, fname)
                for cls, fn, key, ln in pulls_in(p):
                    out[cls].append((fn, key, os.path.basename(p), ln))
    return out

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')          # щоб «→» не спіткнувся на консолі
    for cls, rows in sorted(scan(sys.argv[1]).items()):
        print(f"{cls}: справжній список залежностей = {sorted({k for _, k, _, _ in rows})}")
        for fn, key, f, ln in rows:
            print(f"    {f}:{ln}  {fn}()  →  '{key}'")
