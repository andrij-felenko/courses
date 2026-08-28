class BlueGreenDeploymentEngine:
    """
    Головний механізм координації синьо-зеленого розгортання.
    """

    def __init__(self, config: DeploymentConfig, router: L7TrafficRouter) -> None:
        self.config = config
        self.router = router
        self.phase = DeploymentPhase.IDLE

        # Початковий стан: Blue активний з версією v1.0.0
        self.environments: Dict[EnvironmentRole, EnvironmentState] = {
            EnvironmentRole.BLUE: EnvironmentState(
                role=EnvironmentRole.BLUE,
                version="v1.0.0",
                endpoints=[
                    Endpoint("10.0.1.11", 8080, "v1.0.0"),
                    Endpoint("10.0.1.12", 8080, "v1.0.0"),
                ],
                is_active=True,
                is_warm=True,
            ),
            EnvironmentRole.GREEN: EnvironmentState(
                role=EnvironmentRole.GREEN,
                version="v1.0.0",
                endpoints=[],
                is_active=False,
                is_warm=False,
            ),
        }

    def _get_target_role(self) -> EnvironmentRole:
        """Повертає роль неактивного середовища (куди розгортається реліз)."""
        return (EnvironmentRole.GREEN 
                if self.router.active_role == EnvironmentRole.BLUE 
                else EnvironmentRole.BLUE)

    def _get_active_role(self) -> EnvironmentRole:
        """Повертає роль поточного активного продакшн-середовища."""
        return self.router.active_role

    async def execute_deployment(self) -> bool:
        """
        Головна точка входу для запуску синьо-зеленого циклу розгортання.
        Повертає True, якщо оновлення успішне, або False, якщо стався відкат.
        """
        target_role = self._get_target_role()
        active_role = self._get_active_role()

        logger.info("=== ЗАПУСК СИНЬО-ЗЕЛЕНОГО ДЕПЛОЮ ДЛЯ %s ===", self.config.app_name)
        logger.info("Активне середовище: %s (%s) | Цільове середовище: %s (нова версія: %s)",
                    active_role.value, self.environments[active_role].version,
                    target_role.value, self.config.target_version)

        try:
            # 1. Фаза виділення ресурсів (Provisioning)
            self.phase = DeploymentPhase.PROVISIONING
            await self._phase_provision(target_role)

            # 2. Фаза синтетичного прогріву (Warmup)
            self.phase = DeploymentPhase.WARMING_UP
            await self._phase_warmup(target_role)

            # 3. Фаза димового тестування (Smoke Testing)
            self.phase = DeploymentPhase.SMOKE_TESTING
            if not await self._phase_smoke_test(target_role):
                raise RuntimeError("Димові тести на цільовому середовищі провалено!")

            # 4. Фаза атомарного перемикання трафіку (Cutover)
            self.phase = DeploymentPhase.CUTOVER
            await self._phase_cutover(target_role, active_role)

            # 5. Фаза моніторингу вистоювання (Soak Monitoring)
            self.phase = DeploymentPhase.SOAK_MONITORING
            soak_passed = await self._phase_soak_monitor(target_role)

            if not soak_passed:
                logger.error("Критичні метрики якості деградували під час вистоювання!")
                await self._trigger_emergency_rollback(active_role, target_role)
                self.phase = DeploymentPhase.FAILED
                return False

            # 6. Успішне завершення (Promoted)
            self.phase = DeploymentPhase.PROMOTED
            await self._phase_promote(target_role, active_role)
            logger.info("=== СИНЬО-ЗЕЛЕНИЙ ДЕПЛОЙ УСПІШНО ЗАВЕРШЕНО ===")
            return True

        except Exception as exc:
            logger.exception("Аварійна ситуація під час деплою: %s", str(exc))
            if self.phase in (DeploymentPhase.CUTOVER, DeploymentPhase.SOAK_MONITORING):
                await self._trigger_emergency_rollback(active_role, target_role)
            self.phase = DeploymentPhase.FAILED
            return False

    async def _phase_provision(self, target_role: EnvironmentRole) -> None:
        """Створює нові вузли з новим артефактом у цільовому середовищі."""
        logger.info("[ФАЗА 1/6: PROVISIONING] Розгортання версії %s у середовищі %s...",
                    self.config.target_version, target_role.value)
        await asyncio.sleep(0.5)

        # Реєстрація нових IP-адрес
        new_endpoints = [
            Endpoint("10.0.2.21", 8080, self.config.target_version),
            Endpoint("10.0.2.22", 8080, self.config.target_version),
        ]
        self.environments[target_role] = EnvironmentState(
            role=target_role,
            version=self.config.target_version,
            endpoints=new_endpoints,
            is_active=False,
            is_warm=False,
        )
        logger.info("[PROVISIONING] Створено %d нових вузлів для %s.",
                    len(new_endpoints), target_role.value)

    async def _phase_warmup(self, target_role: EnvironmentRole) -> None:
        """Виконує синтетичні запити для заповнення локальних кешів та прогріву пулів."""
        logger.info("[ФАЗА 2/6: WARMUP] Прогрів кешів та ініціалізація пулів з'єднань (%d запитів)...",
                    self.config.warmup_requests_count)
        
        # Симуляція паралельного потоку запитів
        tasks = [
            self.router.route_preview_request(target_role, "/warmup/prime-cache")
            for _ in range(self.config.warmup_requests_count)
        ]
        results = await asyncio.gather(*tasks)
        avg_lat = sum(r[1] for r in results) / len(results)
        self.environments[target_role].is_warm = True
        logger.info("[WARMUP] Середовище %s прогріто. Середній час відповіді під час прогріву: %.2f мс.",
                    target_role.value, avg_lat)

    async def _phase_smoke_test(self, target_role: EnvironmentRole) -> bool:
        """Перевіряє критичні бізнес-маршрути перед відкриттям публічного доступу."""
        logger.info("[ФАЗА 3/6: SMOKE TEST] Валідація бізнес-контрактів та зондів працездатності...")
        test_routes = ["/healthz", "/api/v1/catalog", "/api/v1/auth/validate"]

        for route in test_routes:
            status_code, lat = await self.router.route_preview_request(target_role, route)
            if status_code != 200:
                logger.error("[SMOKE TEST] Маршрут %s повернув статус %d на %s!",
                             route, status_code, target_role.value)
                return False
            logger.info("[SMOKE TEST] Маршрут %s: HTTP 200 OK (%.2f мс)", route, lat)
        return True

    async def _phase_cutover(self, target_role: EnvironmentRole, old_role: EnvironmentRole) -> None:
        """Виконує миттєве перемикання L7-роутера та запускає дренаж старого середовища."""
        logger.info("[ФАЗА 4/6: CUTOVER] Атомарне перемикання трафіку на %s...", target_role.value)
        await self.router.switch_active_target(target_role)
        self.environments[target_role].is_active = True
        self.environments[old_role].is_active = False

        # Запуск асинхронного дренажу з'єднань у фоні
        asyncio.create_task(self.router.execute_drain(old_role, self.config.drain_timeout_seconds))

    async def _phase_soak_monitor(self, target_role: EnvironmentRole) -> bool:
        """
        Спостерігає за станом нового середовища протягом soak_duration_seconds.
        Перевіряє частоту помилок та затримки p99 кожну секунду.
        """
        logger.info("[ФАЗА 5/6: SOAK MONITORING] Спостереження за живим трафіком протягом %.1f с...",
                    self.config.soak_duration_seconds)
        
        start = time.monotonic()
        while time.monotonic() - start < self.config.soak_duration_seconds:
            await asyncio.sleep(1.0)
            
            # Симуляція отримання метрик із Prometheus
            current_err_rate, current_p99 = await self._fetch_live_metrics(target_role)
            self.environments[target_role].error_rate_percent = current_err_rate
            self.environments[target_role].p99_latency_ms = current_p99

            logger.info("[SOAK METRICS] %s -> Помилки: %.2f%% (ліміт: %.1f%%) | p99: %.1f мс (ліміт: %.1f мс)",
                        target_role.value, current_err_rate, self.config.max_allowed_error_rate,
                        current_p99, self.config.max_allowed_p99_latency_ms)

            if current_err_rate > self.config.max_allowed_error_rate:
                logger.error("[SOAK VIOLATION] Перевищено ліміт частоти помилок!")
                return False

            if current_p99 > self.config.max_allowed_p99_latency_ms:
                logger.error("[SOAK VIOLATION] Перевищено ліміт затримки p99!")
                return False

        return True

    async def _trigger_emergency_rollback(self, safe_role: EnvironmentRole, failed_role: EnvironmentRole) -> None:
        """
        АВАРІЙНИЙ ВІДКАТ ЗА O(1) ЧАС.
        Миттєво перемикає роутер назад на безпечне середовище, яке збереглося в пам'яті.
        """
        self.phase = DeploymentPhase.ROLLING_BACK
        logger.critical("!!! АВАРІЙНИЙ ВІДКАТ: МИТТЄВЕ ПЕРЕМИКАННЯ ТРАФІКУ НАЗАД НА %s !!!",
                        safe_role.value.upper())
        await self.router.switch_active_target(safe_role)
        self.environments[safe_role].is_active = True
        self.environments[failed_role].is_active = False
        logger.info("[ROLLBACK] Трафік повернуто на %s. Пошкоджене середовище %s ізольовано для аналізу.",
                    safe_role.value, failed_role.value)

    async def _phase_promote(self, target_role: EnvironmentRole, old_role: EnvironmentRole) -> None:
        """Остаточне закріплення релізу та переведення старого середовища в режим очікування."""
        logger.info("[ФАЗА 6/6: PROMOTE] Реліз версії %s у середовищі %s офіційно затверджено.",
                    self.config.target_version, target_role.value)
        logger.info("[PROMOTE] Старе середовище %s переведено у статус Standby для наступного релізу.",
                    old_role.value)

    async def _fetch_live_metrics(self, role: EnvironmentRole) -> Tuple[float, float]:
        """Симуляція збору метрик реального часу з системи спостережуваності."""
        # У нормальному стані: 0.05% помилок, 45 мс p99
        return 0.05, 45.0
