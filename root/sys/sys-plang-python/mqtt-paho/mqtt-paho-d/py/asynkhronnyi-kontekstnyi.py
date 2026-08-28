import asyncio
from aiomqtt import Client, MqttError

async def main():
    async with Client(
        hostname="mqtt.internal.iot",
        port=8883,
        identifier="async-ingestion-srv",
        clean_session=False
    ) as client:
        # Асинхронне оформлення підписки
        await client.subscribe("tenants/+/devices/+/telemetry", qos=1)

        # Асинхронне вичитування потоку повідомлень
        async for message in client.messages:
            print(f"Отримано топік {message.topic}: {len(message.payload)} байт")
            # Тут можна безпечно виконувати неблокувальні await-виклики:
            # await db_pool.execute("INSERT INTO ...", message.payload)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except MqttError as err:
        print(f"Помилка мережевого клієнта MQTT: {err}")
