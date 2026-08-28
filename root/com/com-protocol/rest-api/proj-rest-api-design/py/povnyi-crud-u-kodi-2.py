@app.put('/tasks/{task_id}')
def replace_task(task_id: int, body: TaskReplace) -> Task:   # усі поля обов'язкові
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail='task not found')
    task = Task(id=task_id, **body.model_dump())
    tasks[task_id] = task                                    # заміна ЦІЛКОМ
    return task

@app.patch('/tasks/{task_id}')
def update_task(task_id: int, body: TaskPatch) -> Task:
    current = tasks.get(task_id)
    if current is None:
        raise HTTPException(status_code=404, detail='task not found')
    changes = body.model_dump(exclude_unset=True)            # лише НАЗВАНІ поля
    if not changes:
        raise HTTPException(status_code=400, detail='empty patch')
    updated = current.model_copy(update=changes)             # ЗШИВАННЯ
    tasks[task_id] = updated
    return updated
