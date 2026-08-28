// Пакетна функція для зв'язку 1-до-багатьох: Post -> Comments[]
async function batchGetCommentsByPostIds(
  postIds: ReadonlyArray<string>,
  db: DatabaseConnection
): Promise<Array<Comment[]>> {
  // 1. Отримуємо всі коментарі для всіх постів одним запитом
  const rows = await db.query<CommentRow>(
    "SELECT id, post_id, content, author_id FROM comments WHERE post_id IN (?)",
    [postIds]
  );

  // 2. Групуємо коментарі у словник за post_id
  const commentsByPostId = new Map<string, Comment[]>();
  for (const postId of postIds) {
    commentsByPostId.set(postId, []);
  }

  for (const row of rows) {
    const list = commentsByPostId.get(row.post_id);
    if (list !== undefined) {
      list.push({
        id: row.id,
        content: row.content,
        authorId: row.author_id
      });
    }
  }

  // 3. Повертаємо масив списків у ТОЧНОМУ порядку вихідних postIds
  return postIds.map((postId) => commentsByPostId.get(postId) ?? []);
}
