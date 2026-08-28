def evaluate(node, env):
    match node:
        case ('var', name):  return env[name]
        case ('not', a):     return not evaluate(a, env)
        case ('and', a, b):  return evaluate(a, env) and evaluate(b, env)
        case ('or', a, b):   return evaluate(a, env) or evaluate(b, env)
        case ('imp', a, b):  return (not evaluate(a, env)) or evaluate(b, env)

def variables(node):
    match node:
        case ('var', name): return {name}
        case ('not', a):    return variables(a)
        case (_, a, b):     return variables(a) | variables(b)
