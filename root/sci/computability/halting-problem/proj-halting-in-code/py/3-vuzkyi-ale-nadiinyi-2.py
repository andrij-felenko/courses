def classify(loop):
    body, test = loop.body, loop.test
    exits = any(escapes(st, (ast.Break, ast.Return, ast.Raise)) for st in body)
    calls = any(has_call(st) for st in body)

    # (1) тривіальна нескінченність: while True без жодного виходу й виклику
    if isinstance(test, ast.Constant) and test.value is True:
        if not exits and not calls:
            return "LOOPS", "while True — жодного виходу, жодного виклику"
        return "UNKNOWN", "while True, але є вихід чи виклик — не беруся"

    # (2) простий лічильниковий варіант:  while i {<,<=,>,>=} межа
    if (isinstance(test, ast.Compare) and len(test.ops) == 1
            and isinstance(test.left, ast.Name)):
        i, op, bound = test.left.id, test.ops[0], test.comparators[0]
        if calls:
            return "UNKNOWN", "у тілі виклик — чужа функція могла б не повернутись"
        if any(escapes(st, (ast.Continue,)) for st in body):
            return "UNKNOWN", "є continue — крок може прослизнути"
        if binds(loop, i) != 1:
            return "UNKNOWN", "i змінюється не рівно одну безумовну дію"
        step = next((st for st in body if isinstance(st, ast.AugAssign)
                     and isinstance(st.target, ast.Name) and st.target.id == i), None)
        if step is None:
            return "UNKNOWN", "єдина зміна i — не безумовне i ±= c на верхньому рівні"
        c = step.value
        if not (isinstance(c, ast.Constant) and isinstance(c.value, int) and c.value > 0):
            return "UNKNOWN", "крок не є додатною цілою константою"
        if isinstance(bound, ast.Name) and binds(loop, bound.id) > 0:
            return "UNKNOWN", "межу теж рухають — варіант не сталий"
        up = isinstance(step.op, ast.Add)
        toward = (isinstance(op, (ast.Lt, ast.LtE)) and up) or \
                 (isinstance(op, (ast.Gt, ast.GtE)) and isinstance(step.op, ast.Sub))
        if not toward:
            return "UNKNOWN", "крок веде i ГЕТЬ від межі — може не спинитись"
        return "TERMINATES", "варіант строго спадає до дна, крок %d" % c.value

    return "UNKNOWN", "форма циклу не з тих, що вміє цей інструмент"
