test("офлайн у безпечній зоні — один тихий пуш", () => {
  const bus = spyBus();
  notifyOffline({ device: "Камера-1", zone: "двір", at: T });
  expect(bus.push).toHaveBeenCalledTimes(1);
  expect(bus.sms).not.toHaveBeenCalled();
});

// уся спільна логіка — в одному чистому тесті формули, без каналів і подій:
test.each([["двір", 0], ["спальня", 2], ["сейф-кімната", 3]])(
  "dangerLevel(%s) удень = %i", (zone, lvl) =>
    expect(dangerLevel(zone as string, NOON)).toBe(lvl),
);
test("вночі формула піднімає на щабель", () =>
  expect(dangerLevel("спальня", MIDNIGHT)).toBe(3));
