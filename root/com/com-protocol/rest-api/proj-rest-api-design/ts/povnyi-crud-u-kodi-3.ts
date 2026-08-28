const replaceSchema = {
  body: {
    type: 'object',
    required: ['title', 'done', 'priority'],   // повне представлення — УСІ поля
    additionalProperties: false,
    properties: fields,
  },
};
app.put('/tasks/:id', { schema: replaceSchema }, (req, reply) => {
  const id = Number((req.params as { id: string }).id);
  if (!tasks.has(id)) return reply.code(404).send({ error: 'task not found' });
  const task: Task = { id, ...(req.body as Omit<Task, 'id'>) };
  tasks.set(id, task);                          // заміна ЦІЛКОМ
  reply.send(task);
});

const patchSchema = {
  body: {
    type: 'object',
    minProperties: 1,                           // порожній patch — це помилка
    additionalProperties: false,
    properties: fields,
  },
};
app.patch('/tasks/:id', { schema: patchSchema }, (req, reply) => {
  const id = Number((req.params as { id: string }).id);
  const current = tasks.get(id);
  if (!current) return reply.code(404).send({ error: 'task not found' });
  const updated: Task = { ...current, ...(req.body as Partial<Task>) };   // ЗШИВАННЯ
  tasks.set(id, updated);
  reply.send(updated);
});
