// СЕРВЕР DH: статус для тих, хто ОПИТУЄ (телефон тягне сам)
app.get("/jobs/:id", async (req, res) => {
  const j = await jobs.get(req.params.id);
  res.json({ status: j.status, ok: j.ok });   // "processing" → ... → "done"
});

// СЕРВЕР DH: коли задача завершилась — ШТОВХАЄМО вебхук тим, хто зареєстрував адресу
async function onFirmwareDone(job) {
  for (const url of await hooks.for(job.home)) {
    const body = JSON.stringify({ event: "firmware.updated", home: job.home, ok: job.ok });
    await deliver(url, body, sign(body, secret)); // з підписом + повтор при збої (див. проєкт)
  }
}

// ТЕЛЕФОН: опитування з відступом, поки екран відкритий
async function pollUntilDone(id) {
  let wait = 1000;
  for (;;) {
    const r = await (await fetch(`/jobs/${id}`)).json();
    if (r.status === "done") return r;              // дізналися результат
    await sleep(wait);
    wait = Math.min(wait * 2, 15000);               // відступ, щоб не бити щосекунди
  }
}
