// Контрактний тест: істинний для БУДЬ-ЯКОГО ReadableList.
// Приймає фабрику, щоб прогнати той самий тест на кожній реалізації.
function readableContract(
  name: string,
  make: (init: number[]) => ReadableList<number>,
): void {
  test(`${name}: читання за контрактом ReadableList`, () => {
    const list = make([10, 20, 30]);
    expect(list.size()).toBe(3);          // постумова size
    expect(list.get(0)).toBe(10);         // постумова get
    expect(list.get(2)).toBe(30);
  });
}

// Той самий контракт — на обох реалізаціях. Обидві мусять пройти.
readableContract("ArrayList", (init) => {
  const l = new ArrayList<number>();
  for (const x of init) l.add(x);
  return l;
});
readableContract("ImmutableList", (init) => new ImmutableList<number>(init));
