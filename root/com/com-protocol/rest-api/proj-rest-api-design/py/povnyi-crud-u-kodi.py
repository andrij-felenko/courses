@app.get('/tasks')
def list_tasks() -> list[Task]:
    return list(tasks.values())                            # 200 автоматично

@app.get('/tasks/{task_id}')
def get_task(task_id: int) -> Task:                        # не число в id → 422 сам собою
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail='task not found')
    return task
