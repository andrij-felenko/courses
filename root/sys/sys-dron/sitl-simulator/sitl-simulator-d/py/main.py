import asyncio
from mavsdk import System

async def run_simulation_mission():
    drone = System()
    print("[Python SITL Client] Підключення до симулятора на udp://:14540...")
    await drone.connect(system_address="udp://:14540")

    print("Очікування з'єднання з автопілотом...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Автопілот виявлено на лінії!")
            break

    print("Очікування готовності навігаційного фільтра EKF...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("Фільтр EKF зійшовся, GPS зафіксовано.")
            break

    print("Озброєння моторів...")
    await drone.action.arm()

    print("Зліт на 15 метрів...")
    await drone.action.set_takeoff_altitude(15.0)
    await drone.action.takeoff()

    await asyncio.sleep(10)

    print("Виконання повернення на точку старту (RTL)...")
    await drone.action.return_to_launch()

if __name__ == "__main__":
    asyncio.run(run_simulation_mission())
