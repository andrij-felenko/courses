import ast

def escapes(node, kinds, mine=True):
    """Чи є в node вихід одного з типів kinds, що належить НАШОМУ циклу?
    break/continue гілкуються до найближчого циклу (тому mine гасне у вкладеному);
    return/raise виносять із функції завжди."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
        return False                                   # інша область видимості
    if isinstance(node, kinds):
        if isinstance(node, (ast.Break, ast.Continue)):
            if mine:
                return True
        else:
            return True
    inner = isinstance(node, (ast.For, ast.While, ast.AsyncFor))
    return any(escapes(ch, kinds, mine and not inner) for ch in ast.iter_child_nodes(node))

def has_call(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
        return False
    if isinstance(node, (ast.Call, ast.Await)):
        return True
    return any(has_call(ch) for ch in ast.iter_child_nodes(node))

def binds(node, name):
    """Скільки разів тіло переприсвоює `name` (=, +=, ціль for)."""
    n = 0
    for ch in ast.iter_child_nodes(node):
        if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        if isinstance(ch, ast.Assign):
            n += sum(isinstance(t, ast.Name) and t.id == name for t in ch.targets)
        elif isinstance(ch, ast.AugAssign):
            n += int(isinstance(ch.target, ast.Name) and ch.target.id == name)
        elif isinstance(ch, (ast.For, ast.AsyncFor)):
            n += int(isinstance(ch.target, ast.Name) and ch.target.id == name)
        n += binds(ch, name)
    return n
