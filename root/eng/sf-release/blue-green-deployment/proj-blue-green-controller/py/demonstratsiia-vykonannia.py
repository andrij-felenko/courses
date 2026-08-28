async def run_demonstration():
    # 1. Успішний сценарій
    router = L7TrafficRouter()
    config_ok = DeploymentConfig(
        app_name="BillingGateway",
        target_version="v1.1.0",
        warmup_requests_count=10,
        soak_duration_seconds=3.0,
        max_allowed_error_rate=1.0,
        drain_timeout_seconds=2.0
    )
    engine = BlueGreenDeploymentEngine(config_ok, router)
    logger.info("================ ТЕСТ 1: УСПІШНИЙ РЕЛІЗ ================")
    success = await engine.execute_deployment()
    assert success is True
    assert router.active_role == EnvironmentRole.GREEN

    # 2. Сценарій відкату через деградацію SLI
    logger.info("\n================ ТЕСТ 2: АВАРІЙНИЙ ВІДКАТ ================")
    config_fail = DeploymentConfig(
        app_name="BillingGateway",
        target_version="v1.2.0-broken",
        warmup_requests_count=5,
        soak_duration_seconds=3.0,
        max_allowed_error_rate=1.0,
        drain_timeout_seconds=2.0
    )
    engine_fail = BlueGreenDeploymentEngine(config_fail, router)

    # Підміна збору метрик для симуляції збою під навантаженням
    async def broken_metrics(role: EnvironmentRole) -> Tuple[float, float]:
        return 8.5, 450.0  # 8.5% помилок і 450 мс затримка
    engine_fail._fetch_live_metrics = broken_metrics

    success_fail = await engine_fail.execute_deployment()
    assert success_fail is False
    # Перевірка, що роутер миттєво повернувся на стабільний Green v1.1.0
    assert router.active_role == EnvironmentRole.GREEN
    logger.info("Тести завершено. Контролер продемонстрував нульовий простій та миттєвий відкат.")


if __name__ == "__main__":
    asyncio.run(run_demonstration())
