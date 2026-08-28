test("резолвер Post.author пакетує виклики і усуває N+1", async () => {
  let batchExecutionCount = 0;
  
  const mockBatchFn = async (ids: ReadonlyArray<string>) => {
    batchExecutionCount++;
    return ids.map((id) => ({ id, name: `User ${id}`, avatarUrl: "http://..." }));
  };

  const testLoader = new DataLoader(mockBatchFn);
  const context = { loaders: { userLoader: testLoader } };

  // Імітуємо виконання 10 резолверів для 10 постів (автори 1, 2, 1, 3, 2...)
  const promises = [
    resolvers.Post.author({ author_id: "1" }, {}, context),
    resolvers.Post.author({ author_id: "2" }, {}, context),
    resolvers.Post.author({ author_id: "1" }, {}, context),
    resolvers.Post.author({ author_id: "3" }, {}, context),
  ];

  const authors = await Promise.all(promises);

  // Перевіряємо результати
  expect(authors).toHaveLength(4);
  expect(authors[0].id).toBe("1");
  expect(authors[2].id).toBe("1");

  // КРИТИЧНА ПЕРЕВІРКА: пакетна функція викликалася РІВНО ОДИН РАЗ
  expect(batchExecutionCount).toBe(1);
});
