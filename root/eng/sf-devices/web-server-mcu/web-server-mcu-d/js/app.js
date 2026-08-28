// Хендлери на Express: гілка /static/* і параметр запиту /led?state=on.
app.get("/static/*", (req, res) => {         // '*' ловить усю гілку
  const name = req.params[0];                // "app.js" — уже без префікса
  sendFileFromFs(res, name);                 // читаємо файл і віддаємо (нижче)
});

app.get("/led", (req, res) => {              // /led?state=on
  const state = req.query.state;             // окремий ключ query string
  if (state !== undefined)
    setLed(state === "on");                  // вмикаємо/вимикаємо
  res.send("ok");
});
