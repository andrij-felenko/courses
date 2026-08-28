async function polymorphicNodeBatchLoader(
  globalIds: ReadonlyArray<string>,
  context: ExecutionContext
): Promise<Array<Node | Error>> {
  // 1. Групуємо ключі за типом сутності
  const userIds: string[] = [];
  const postIds: string[] = [];
  const commentIds: string[] = [];

  for (const gid of globalIds) {
    const [type, rawId] = gid.split(":");
    if (type === "User") userIds.push(rawId);
    else if (type === "Post") postIds.push(rawId);
    else if (type === "Comment") commentIds.push(rawId);
  }

  // 2. Паралельно викликаємо спеціалізовані лоадери для кожного типу
  const [users, posts, comments] = await Promise.all([
    context.loaders.userLoader.loadMany(userIds),
    context.loaders.postLoader.loadMany(postIds),
    context.loaders.commentLoader.loadMany(commentIds)
  ]);

  // 3. Індексуємо знайдені сутності в єдиний Map
  const nodeMap = new Map<string, Node>();
  userIds.forEach((id, i) => {
    const u = users[i];
    if (!(u instanceof Error)) nodeMap.set(`User:${id}`, u);
  });
  postIds.forEach((id, i) => {
    const p = posts[i];
    if (!(p instanceof Error)) nodeMap.set(`Post:${id}`, p);
  });
  commentIds.forEach((id, i) => {
    const c = comments[i];
    if (!(c instanceof Error)) nodeMap.set(`Comment:${id}`, c);
  });

  // 4. Повертаємо результати у вихідному порядку вхідних globalIds
  return globalIds.map((gid) => nodeMap.get(gid) ?? new Error(`Вузол ${gid} не знайдено`));
}
