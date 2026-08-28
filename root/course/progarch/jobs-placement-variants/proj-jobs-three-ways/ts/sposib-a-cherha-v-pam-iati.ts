test("черга в памʼяті губить роботу на рестарті", () => {
  let q = new InMemoryQueue();
  q.enqueue("transcode", { clipId: 42 });     // кліп 42 залито, задача стоїть
  expect(q.depth()).toBe(1);

  // Деплой, падіння, рестарт = НОВИЙ процес = НОВА, порожня черга:
  q = new InMemoryQueue();

  expect(q.depth()).toBe(0);   // задача зникла. Кліп у базі є, борг — випарувався.
});
