seen: dict[str, Task] = {}                          # ключ → перший результат

@app.post('/tasks', status_code=201)
def create_task(body: TaskIn, response: Response,
                idempotency_key: str | None = Header(default=None)) -> Task:
    global _next_id
    if idempotency_key and idempotency_key in seen:
        return seen[idempotency_key]                # повертаємо перший результат
    task = Task(id=_next_id, **body.model_dump())
    tasks[task.id] = task
    _next_id += 1
    if idempotency_key:
        seen[idempotency_key] = task
    response.headers['Location'] = f'/tasks/{task.id}'
    return task
