from fastapi import Depends, Header, HTTPException, status

async def verify_device_token(x_device_token: str = Header(...)) -> str:
    # Перевірка криптографічного токена датчика в асинхронному кеші
    if not await token_cache.is_valid(x_device_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device hardware token"
        )
    return x_device_token

@app.post("/api/v1/telemetry")
async def record_telemetry(
    reading: SensorReading,
    token: str = Depends(verify_device_token),
    db: AsyncSession = Depends(get_db_session)
):
    await db.save(reading)
    return {"status": "accepted"}
