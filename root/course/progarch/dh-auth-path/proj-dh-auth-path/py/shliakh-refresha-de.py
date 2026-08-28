# ── Шлях рефреша на шлюзі: ТУТ виключеному членові кажуть «ні» ──
async def refresh(req) -> dict:
    refresh_id = read_refresh_cookie(req)
    record = await refresh_store.get(refresh_id)       # непрозорий id → правда в сторі
    if record is None:
        raise Http(401)                                # refresh відкликано/протух → нового access не дамо

    if await revocations.is_revoked(record.subject_id, record.home_id):  # виключений із дому?
        raise Http(403)                                # орган відкликання каже «ні»

    return {"access": issue_access(record)}            # інакше — свіжий короткий access
