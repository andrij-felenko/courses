import math

INF = float("inf")
def log(p):                              # −inf замість краху на log(0)
    return math.log(p) if p > 0 else -INF

states = ["F", "L"]                      # F — чесний кубик, L — шахрайський

log_pi = {"F": log(0.5), "L": log(0.5)}          # з чого починаємо

logA = {                                 # підміна кубика між кидками
    "F": {"F": log(0.90), "L": log(0.10)},
    "L": {"F": log(0.20), "L": log(0.80)},
}
logB = {                                 # яка грань з якого кубика
    "F": {f: log(1/6) for f in range(1, 7)},         # чесний: усі грані рівні
    "L": {1: log(.08), 2: log(.08), 3: log(.08),     # шахрайський: шістка
          4: log(.08), 5: log(.08), 6: log(.60)},    #   набагато частіша
}

def branch(s, s2, face):                 # вартість одного ребра ґратки
    return logA[s][s2] + logB[s2][face]  # лог(перехід) + лог(породження)

def viterbi(obs):
    M  = {s: log_pi[s] + logB[s][obs[0]] for s in states}   # старт: π + перша грань
    bp = []                                                 # вказівники назад по тактах
    for face in obs[1:]:
        newM, step = {}, {}
        for s2 in states:                # для кожного нового стану s2:
            best = max(states, key=lambda s: M[s] + branch(s, s2, face))  # COMPARE
            newM[s2] = M[best] + branch(best, s2, face)                   # ADD
            step[s2] = best                                              # SELECT
        M, bp = newM, bp + [step]
    last = max(states, key=lambda s: M[s])   # найкращий кінцевий стан
    path = [last]
    for step in reversed(bp):                # TRACEBACK: іти вказівниками назад
        last = step[last]
        path.append(last)
    return path[::-1], max(M.values())

obs = [2, 4, 1, 3, 6, 5, 2, 1,  6, 6, 6, 6, 6, 6,  3, 1, 4, 2, 5, 3]

path, score = viterbi(obs)
greedy = [max(states, key=lambda s: logB[s][f]) for f in obs]  # кожен кидок окремо

print("кидок  ", " ".join(map(str, obs)))
print("Вітербі", " ".join(path))
print("пожадл.", " ".join(greedy))
print("лог-правдоподібність:", round(score, 3))
