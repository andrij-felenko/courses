function* fibonacci() {
  let [a, b] = [0, 1];
  while (true) {           // нескінченний генератор
    yield a;               // віддали a й заснули тут
    [a, b] = [b, a + b];   // прокинулись — рахуємо далі
  }
}

const it = fibonacci();
console.log(it.next().value, it.next().value, it.next().value);   // 0 1 1
