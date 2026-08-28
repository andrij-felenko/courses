class L7TrafficRouter:
    """
    Інкапсулює керування L7-маршрутизатором (Envoy, NGINX Upstream API, HAProxy Socket).
    Забезпечує атомарне перемикання бекенд-пулів за O(1) час.
    """

    def __init__(self) -> None:
        self._active_role: EnvironmentRole = EnvironmentRole.BLUE
        self._preview_role: Optional[EnvironmentRole] = None
        self._drain_in_progress: Dict[EnvironmentRole, bool] = {
            EnvironmentRole.BLUE: False,
            EnvironmentRole.GREEN: False,
        }

    @property
    def active_role(self) -> EnvironmentRole:
        return self._active_role

    async def switch_active_target(self, target_role: EnvironmentRole) -> None:
        """Атомарно перемикає 100% публічного трафіку на обраний пул."""
        old_role = self._active_role
        if old_role == target_role:
            logger.warning("Цільовий пул %s вже є активним.", target_role.value)
            return

        logger.info("=== [L7 ROUTER] ПЕРЕМИКАННЯ ТРАФІКУ: %s -> %s ===",
                    old_role.value.upper(), target_role.value.upper())
        
        # Симуляція запису команди в сокет керування балансувальника (O(1) операція)
        await asyncio.sleep(0.05)
        self._active_role = target_role
        self._drain_in_progress[old_role] = True
        logger.info("[L7 ROUTER] Публічний трафік успішно переведено на %s. Пул %s переведено в режим дренажу.",
                    target_role.value, old_role.value)

    async def execute_drain(self, role: EnvironmentRole, timeout: float) -> None:
        """Очікує завершення обробки активних відкритих з'єднань на старому пулі."""
        logger.info("[L7 ROUTER] Початок дренажу відкритих з'єднань для %s (таймаут %.1f с)...",
                    role.value, timeout)
        # Балансувальник надсилає заголовок 'Connection: close' або кадр GOAWAY в HTTP/2
        await asyncio.sleep(timeout)
        self._drain_in_progress[role] = False
        logger.info("[L7 ROUTER] Дренаж пулу %s успішно завершено. Пул перебуває в режимі Standby.",
                    role.value)

    async def route_preview_request(self, role: EnvironmentRole, path: str) -> Tuple[int, float]:
        """Спрямовує службовий запит безпосередньо на тестований пул в обхід публічного трафіку."""
        start_time = time.monotonic()
        # Симуляція виконання мережевого HTTP-запиту до тестованого бекенду
        await asyncio.sleep(0.01)
        elapsed_ms = (time.monotonic() - start_time) * 1000.0
        return 200, elapsed_ms
