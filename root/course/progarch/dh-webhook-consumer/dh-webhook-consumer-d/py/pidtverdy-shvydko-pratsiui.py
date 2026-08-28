# Тонкий приймач: перевір → запиши → у чергу → ACK. Жодної важкої роботи інлайн.
@app.post("/hooks/acme-lock")
async def receive(req: Request):
    raw = await req.body()
    if not verify(raw, req.headers.get("x-acme-signature", ""), SECRET):
        return Response(status_code=400)              # не той підпис — далі не читаємо
    event = json.loads(raw)
    if await inbox.record(event["id"]):               # True, якщо id новий
        await queue.enqueue("lock-event", event)      # справжня робота — потім, у черзі
    return Response(status_code=200)                   # ACK за десятки мс
