app.get('/tasks', (_req, reply) => {
  reply.send([...tasks.values()]);                        // 200 автоматично
});

app.get('/tasks/:id', (req, reply) => {
  const id = Number((req.params as { id: string }).id);
  const task = tasks.get(id);
  if (!task) return reply.code(404).send({ error: 'task not found' });
  reply.send(task);
});
