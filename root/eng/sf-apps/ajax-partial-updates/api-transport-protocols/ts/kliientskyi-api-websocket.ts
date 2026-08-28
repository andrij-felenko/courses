const ws = new WebSocket("wss://server.example.com/socket");
ws.binaryType = "arraybuffer";

ws.onopen = () => {
  // Відправлення текстового повідомлення
  ws.send(JSON.stringify({ action: "SUBSCRIBE", channel: "telemetry" }));
};

ws.onmessage = (event: MessageEvent) => {
  if (typeof event.data === "string") {
    const json = JSON.parse(event.data);
    handleTextMessage(json);
  } else if (event.data instanceof ArrayBuffer) {
    const view = new DataView(event.data);
    handleBinaryFrame(view);
  }
};

ws.onclose = (event: CloseEvent) => {
  console.log(`Сокет закрито: код=${event.code}, причина=${event.reason}, чисте=${event.wasClean}`);
};

ws.onerror = (event: Event) => {
  console.error("Помилка транспортного рівня WebSocket", event);
};
