from enum import Enum, auto


class Role(Enum):
    STANDBY   = auto()    # ми резерв, чекаємо
    PRIMARY   = auto()    # ми головний, виконуємо роль
    PROMOTING = auto()    # ми в процесі підняття (тут беремо оренду/кворум)
    REJOINING = auto()    # ми колишній головний, доганяємо стан після оживлення


# Реакції на події, які реалізує конкретна система (заглушки-приклади):
#   acquire_lease_or_quorum() -> int | None  — взяти оренду, видати токен
#   start_serving(token)                     — почати виконувати роль
#   stop_serving()                           — припинити виконувати роль
#   storage_current_token() -> int           — найбільший токен, що бачило сховище

class Failover:
    def __init__(self, start: Role, now_ms: int):
        self.role = start
        self.peer = NodeHealth(now_ms)   # монітор ЧУЖОГО серцебиття (за ким стежимо)
        self.fence_token = 0             # наш поточний токен огорожі (див. нижче)
        self.promoting_since_ms = 0      # коли почали підніматися (щоб не зависнути)

    # Головний тик автомата: викликається періодично на РЕЗЕРВНОМУ вузлі.
    # now_ms — монотонний час; peer_beat=True, якщо цим тиком прийшов удар
    # від головного.
    def tick(self, now_ms: int, peer_beat: bool) -> None:
        if peer_beat:
            self.peer.on_beat(now_ms)
        self.peer.tick(now_ms)

        if self.role is Role.STANDBY:
            # головний мовчить достатньо довго -> пробуємо піднятися
            if self.peer.health is Health.DOWN:
                self.role = Role.PROMOTING
                self.promoting_since_ms = now_ms

        elif self.role is Role.PROMOTING:
            # КЛЮЧОВА межа: піднятися можна ЛИШЕ взявши оренду/кворум.
            # Це і є заслін розколу мозку — без цього кроку два вузли
            # спокійно піднялися б удвох.
            token = acquire_lease_or_quorum()
            if token is not None:
                self.fence_token = token
                start_serving(token)
                self.role = Role.PRIMARY
            # не взяли оренду -> лишаємось PROMOTING і пробуємо наступним тиком;
            # якщо головний живий і тримає оренду, ми НІКОЛИ не піднімемось

        elif self.role is Role.PRIMARY:
            # ми головний; окремо стежимо, чи не втратили оренду (нижче)
            pass

        elif self.role is Role.REJOINING:
            # ми колись були головним, впали, ожили. Роль уже в іншого.
            # Не рвемось назад — доганяємо стан і чекаємо (пастка ляпання).
            pass
