import random

N = 200   # усього прикладів
K = 5     # число блоків

# Твої функції моделі (заглушки під конкретний алгоритм):
#   train    — навчити на вибраних індексах;
#   accuracy — частка правильних на вибраних індексах.

order = list(range(N))   # порядок прикладів 0..N-1
random.shuffle(order)    # перемішали РАЗ наперед

def cross_validate():
    fold_size = N // K            # 200 // 5 = 40 у блоці
    total = 0.0

    for f in range(K):
        lo = f * fold_size        # межі f-го блоку
        hi = lo + fold_size

        test      = order[lo:hi]                    # цей блок — «іспит»
        train_idx = order[:lo] + order[hi:]         # решта — навчання

        train(train_idx)                            # навчаємо з нуля
        a = accuracy(test)                          # міряємо на іспиті
        total += a
        print(f"прохід {f + 1}: {a * 100:.1f}%")

    return total / K              # середнє п'яти чисел
