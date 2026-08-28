def test_offline_safe_zone_one_push():
    bus = spy_bus()
    notify_offline(OfflineEvent(device="Камера-1", zone="двір", at=T))
    assert bus.push == 1
    assert bus.sms == 0

# уся спільна логіка — в одному чистому тесті формули, без каналів і подій:
@pytest.mark.parametrize("zone, lvl", [("двір", 0), ("спальня", 2), ("сейф-кімната", 3)])
def test_danger_level_day(zone, lvl):
    assert danger_level(zone, NOON) == lvl

def test_danger_level_night_bumps():
    assert danger_level("спальня", MIDNIGHT) == 3
