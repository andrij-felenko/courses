from collections import defaultdict

def hopcroft(delta, accept):
    """Класи нерозрізнюваності за O(|Σ|·n·log n). Повертає список блоків."""
    n, k = len(delta), len(delta[0])

    # обернені переходи: inv[a][t] — усі s, що по a йдуть у t
    inv = [defaultdict(list) for _ in range(k)]
    for s in range(n):
        for a in range(k):
            inv[a][delta[s][a]].append(s)

    F = set(accept)
    blocks = [b for b in (F, set(range(n)) - F) if b]
    if len(blocks) == 1:                       # усі стани в одному класі
        return blocks
    where = [0] * n                            # where[s] — індекс блоку стану s
    for i, b in enumerate(blocks):
        for s in b:
            where[s] = i

    # у чергу — лише МЕНША з двох стартових половин (лема про доповнення)
    work = {0 if len(blocks[0]) <= len(blocks[1]) else 1}
    while work:
        splitter = set(blocks[work.pop()])     # знімок: блок ще може подрібнитись
        for a in range(k):
            # згрупувати δ⁻¹(splitter, a) за блоками — торкаємось лише їх
            touched = defaultdict(list)
            for t in splitter:
                for s in inv[a][t]:
                    touched[where[s]].append(s)
            for j, part in touched.items():
                if len(part) == len(blocks[j]):
                    continue                   # блок цілком у splitter — стабільний
                blocks[j] -= set(part)         # Y лишається на місці як Y∖X
                new = len(blocks)
                blocks.append(set(part))       # Y∩X виїжджає в новий блок
                for s in part:
                    where[s] = new
                if j in work:                  # Y ще не оброблений — обидві половини
                    work.add(new)
                else:                          # інакше досить МЕНШОЇ
                    work.add(new if len(blocks[new]) <= len(blocks[j]) else j)
    return blocks
