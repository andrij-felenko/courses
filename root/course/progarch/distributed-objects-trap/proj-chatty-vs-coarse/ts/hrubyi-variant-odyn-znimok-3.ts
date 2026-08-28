const hub = new Hub();
for (let i = 0; i < 30; i++)
  hub.register(new Device(`d${i}`, "lamp", "hall", "on", 80, 1000));

const chatty = new Link();
await renderChatty(hub.ids(), hub, chatty);
const coarse = new Link();
await renderCoarse(hub, coarse, /* now = */ 1030);

console.log(chatty.crossings, coarse.crossings);      // → 150   1
console.log(chatty.costMs(150), coarse.costMs(150));  // → 22500 150   (мс, океан)
