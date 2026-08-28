# Так це рахує скрипт, що складає метадані при збиранні прошивки,
# і так само рахує будь-який інструмент, що читає бортовий журнал.
def fnv1a32(name: str) -> int:
    h = 0x811C9DC5
    for ch in name:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def event_id(component: int, name: str) -> int:
    return (component << 24) | (fnv1a32(name) & 0xFFFFFF)


assert event_id(1, "commander_rtl") == 0x01352CE4
