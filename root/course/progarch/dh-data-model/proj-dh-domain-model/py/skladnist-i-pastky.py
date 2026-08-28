# ✗ АНТИ-МОДЕЛЬ: «усі або ніхто» — і власник лишає дім відчиненим
def go_away_strict(home: Home, locks: dict[str, Lock], gw: DeviceGateway) -> None:
    for id in home.locks:
        out = gw.send_lock(id)
        match out:
            case Acked(state=LockState.LOCKED):
                pass
            case _:
                raise DomainError("не всі замки замкнулися — режим «нікого немає» скасовано")
    # ← гараж офлайн → виняток → дім НЕ замкнено ВЗАГАЛІ
