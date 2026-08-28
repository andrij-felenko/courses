async def handle_charge(request):
    key = request.headers.get("Idempotency-Key")
    if not key:
        return Response("потрібен Idempotency-Key", status=400)

    # Атомарно: або застовпили ключ за собою, або дізналися, що він уже є.
    claimed = await store.insert_if_absent(key)   # False, якщо ключ уже був
    if not claimed:
        saved = await store.get_result(key)        # це повтор
        return Response(saved.body, status=saved.status)

    result = await charge(request.json["amount"])  # робота — рівно раз
    await store.save_result(key, result)
    return Response(result.body, status=result.status)
