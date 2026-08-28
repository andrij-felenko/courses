import sys

# Фітнес-функція радара: новий код не сміє залежати від блипа в HOLD.
# Повертає кількість порушень (0 — складання проходить).
def check_no_hold_deps(module, deps):
    violations = 0
    for dep in deps:
        r = ring_of(dep)
        if r == Ring.HOLD:
            print(f"[радар] {module} тягне '{dep}' — це кільце HOLD, "
                  f"нового на цьому не заводимо", file=sys.stderr)
            violations += 1
        elif r is None:
            # не заборона, а сигнал: технологія взагалі поза радаром —
            # її не оцінювали, тож варто винести на найближчий перегляд
            print(f"[радар] увага: {module} тягне '{dep}', якого нема на радарі",
                  file=sys.stderr)
    return violations
