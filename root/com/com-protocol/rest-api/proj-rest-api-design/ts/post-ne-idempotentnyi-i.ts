const seen = new Map<string, { status: number; body: Task }>();   // ключ → перший результат

app.post('/tasks', { schema: createSchema }, (req, reply) => {
  const key = req.headers['idempotency-key'] as string | undefined;
  if (key && seen.has(key)) {
    const first = seen.get(key)!;
    return reply.code(first.status).send(first.body);   // повертаємо перший результат
  }
  const body = req.body as Omit<Task, 'id'>;
  const task: Task = { id: nextId++, ...body };
  tasks.set(task.id, task);
  if (key) seen.set(key, { status: 201, body: task });
  reply.code(201).header('Location', `/tasks/${task.id}`).send(task);
});
