# Python: AsyncIO gRPC Сервер з підтримкою ротації з'єднань
import asyncio
import grpc

async def serve_ingest(port: int):
    options = [
        ('grpc.max_connection_age_ms', 3600000),         # 1 година до GOAWAY
        ('grpc.max_connection_age_grace_ms', 30000),     # 30 секунд grace period
        ('grpc.keepalive_time_ms', 30000),               # Ping кожні 30 с
        ('grpc.keepalive_timeout_ms', 10000),            # Таймаут відповіді 10 с
        ('grpc.keepalive_permit_without_calls', 1),
    ]
    
    server = grpc.aio.server(options=options)
    server.add_insecure_port(f'[::]:{port}')
    await server.start()
    print(f"gRPC Ingest Server запущено на порту {port}")
    await server.wait_for_termination()
