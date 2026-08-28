# honesty_check.py — чи ЧЕСНО драйвер грає контракт? НЕ контрактні тести й не Pact:
# пробник, що читає I-1..I-6 назад із драйвера й падає, якщо той збрехав.
from device_driver import DeviceDriver, Ok, Err
from fake_device import FakeDevice

FAULTS = {"offline", "timeout"}

# Крізь контракт видно лише read → перевіряємо I-2/I-3/I-6 «чорною скринькою».
def read_honours_contract(d: DeviceDriver) -> None:
    for _ in range(100):
        try:
            r = d.read()
        except Exception as e:                     # I-3: read НЕ сміє кинути крізь межу
            raise AssertionError(f"I-3 зламано: read кинув — {e}")
        match r:
            case Ok(temp_c=t, at=at):
                assert -40 <= t <= 85, f"I-2: temp_c поза [−40,85]: {t}"
                assert at > 1e9, f"I-6: at не схоже на epoch-с: {at}"   # секунди, не мс!
            case Err(reason=reason):
                assert reason in FAULTS, f"I-3: reason поза закритою множиною: {reason}"

# I-4 — про ПРИХОВАНИЙ ефект, якого read не показує; тут треба вікно у фейк.
def command_is_idempotent(f: FakeDevice) -> None:
    f.set_target(21.0)
    w1 = f.writes
    f.set_target(21.0)                             # той самий таргет, ще раз
    assert f.target == 21.0, "I-4: кінцевий стан має бути 21"
    assert f.writes == w1, "I-4: повтор не мав чіпати залізо вдруге"

if __name__ == "__main__":
    fake = FakeDevice()
    read_honours_contract(fake)
    command_is_idempotent(fake)
    print("контракт дотримано: I-1..I-6 чесні ✓")
