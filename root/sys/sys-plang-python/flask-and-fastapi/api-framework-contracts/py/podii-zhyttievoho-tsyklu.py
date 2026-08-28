async def lifespan_handler(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    # Асинхронний старт системних пулів
                    await database_engine.connect()
                    await send({"type": "lifespan.startup.complete"})
                except Exception as exc:
                    await send({"type": "lifespan.startup.failed", "message": str(exc)})
                    return
            elif message["type"] == "lifespan.shutdown":
                # Гарантоване закриття з'єднань і збереження буферів
                await database_engine.disconnect()
                await send({"type": "lifespan.shutdown.complete"})
                return
