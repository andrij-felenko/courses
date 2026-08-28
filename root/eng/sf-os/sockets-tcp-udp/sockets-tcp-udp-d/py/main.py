# чекати дані на двох сокетах одразу, не блокуючись на жодному
import select

# select віддає готові сокети списком; таймаут — прокинутись хоч раз на 5 с
readable, _, _ = select.select([sock_a, sock_b], [], [], 5)
for s in readable:
    if s is sock_a:  # на A є дані — читаємо тільки A
        ...
    elif s is sock_b:  # на B є дані — читаємо тільки B
        ...
