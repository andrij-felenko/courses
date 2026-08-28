const createSchema = {
  body: {
    type: 'object',
    required: ['title'],
    additionalProperties: false,            // жодних зайвих полів (напр. id)
    properties: {
      ...fields,
      done:     { ...fields.done, default: false },      // Fastify підставить усталене
      priority: { ...fields.priority, default: 'normal' },
    },
  },
};

app.post('/tasks', { schema: createSchema }, (req, reply) => {
  const body = req.body as Omit<Task, 'id'>;             // схема вже все перевірила
  const task: Task = { id: nextId++, ...body };
  tasks.set(task.id, task);
  reply.code(201).header('Location', `/tasks/${task.id}`).send(task);
});
