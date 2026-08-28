def viterbi(obs, states, log_pi, logA, logB):
    # M[s] — найкраща лог-правдоподібність шляху, що завершується в стані s
    M = {s: log_pi[s] + logB[s][obs[0]] for s in states}
    back = []                                    # вказівники назад по тактах
    for o in obs[1:]:
        newM, bp = {}, {}
        for s in states:                         # для кожного нового стану s:
            # COMPARE+SELECT: найкращий попередник за метрикою «дійти + перейти»
            best = max(states, key=lambda q: M[q] + logA[q][s])
            newM[s] = M[best] + logA[best][s] + logB[s][o]   # ADD + породження
            bp[s] = best                         # запам'ятати, звідки прийшли
        M, back = newM, back + [bp]
    last = max(states, key=lambda s: M[s])       # найкращий кінцевий стан
    score, path = M[last], [last]
    for bp in reversed(back):                    # TRACEBACK: іти вказівниками
        last = bp[last]
        path.append(last)
    return path[::-1], score
