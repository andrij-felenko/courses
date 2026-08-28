hub = Hub()
for i in range(30):
    hub.register(Device(f"d{i}", "lamp", "hall", "on", 80, 1000))

chatty = Link()
await render_chatty(hub.ids(), hub, chatty)
coarse = Link()
await render_coarse(hub, coarse, now=1030)

print(chatty.crossings, coarse.crossings)         # → 150 1
print(chatty.cost_ms(150), coarse.cost_ms(150))   # → 22500 150   (мс, океан)
