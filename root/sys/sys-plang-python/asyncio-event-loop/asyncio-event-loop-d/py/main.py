async def load_dashboard_data(user_id: int) -> dict:
    async with asyncio.TaskGroup() as tg:
        task_profile = tg.create_task(fetch_user_profile(user_id))
        task_orders = tg.create_task(fetch_user_orders(user_id))
        task_metrics = tg.create_task(fetch_analytics_metrics(user_id))

    # Вихід із блоку 'async with' гарантує, що ВСІ задачі успішно завершилися
    return {
        "profile": task_profile.result(),
        "orders": task_orders.result(),
        "metrics": task_metrics.result(),
    }
