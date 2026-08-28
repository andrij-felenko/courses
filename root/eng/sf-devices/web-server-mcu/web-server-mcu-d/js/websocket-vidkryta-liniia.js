// WebSocket на ws: ловить кадр і сам штовхає показання.
const { WebSocketServer } = require("ws");
const wss = new WebSocketServer({ server });     // поверх того самого сервера

wss.on("connection", (ws) => {                   // рукостискання вже позаду
  ws.on("message", (frame) => handle(frame));    // кожен кадр від браузера
});

// Штовхнути свіже показання ВСІМ підключеним клієнтам (з іншої задачі).
function wsPushTemperature(t) {
  const msg = JSON.stringify({ temp: Number(t.toFixed(1)) });
  for (const ws of wss.clients)                  // сервер сам ініціює відправку
    ws.send(msg);
}
