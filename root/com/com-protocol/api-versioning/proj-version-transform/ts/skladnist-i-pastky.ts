{
  version: "2024-07-15",
  description: "помилка відсутнього ресурсу: 404/type → 400/code",
  downResponse(r) {
    const e = r.body?.error;
    if (e && e.type === "resource_missing") {
      r.status = 400;                 // старий клієнт чекав саме 400
      e.code = "not_found";           // і поле code, а не type
      delete e.type;
    }
    return r;
  },
}
