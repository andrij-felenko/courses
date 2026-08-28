/** Усі слова над alphabet у шортлекс-порядку. Перелік нескінченний. */
function* sigmaStar(alphabet: string[]): Generator<string> {
  const k = alphabet.length;
  for (let n = 0; ; n++) {
    // слова довжини n — це числа 0…kⁿ−1, записані в системі з основою k
    for (let i = 0; i < k ** n; i++) {
      let w = "", rest = i;
      for (let p = 0; p < n; p++) {
        w = alphabet[rest % k] + w;
        rest = Math.floor(rest / k);
      }
      yield w;                       // n = 0 дає рівно одне слово: ε
    }
  }
}

const words = sigmaStar(["a", "b"]);
console.log(Array.from({ length: 8 }, () => words.next().value));
// [ '', 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aaa' ]
