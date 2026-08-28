# один контракт на будь-яку реалізацію Notifier (pytest)
import pytest
from models import Message

def notifier_contract(make):
    async def run() -> None:
        notifier, delivered = make()
        m = Message(to="owner", body="проба")
        await notifier.send(m)
        assert m in delivered()          # мусить з'явитися у стоці
    return run

@pytest.mark.asyncio
async def test_recording():              # чесний — ПРОХОДИТЬ
    n = RecordingNotifier()
    await notifier_contract(lambda: (n, lambda: n.sent))()

@pytest.mark.asyncio
async def test_silent_trap():            # «мовчазний» — ПАДАЄ, і саме так його ловлять
    n = SilentNotifier()
    await notifier_contract(lambda: (n, lambda: []))()
