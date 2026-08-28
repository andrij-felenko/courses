import http from "node:http";

// Найтонша нитка: браузер → API → «черга» → воркер → сховище → читання назад.
// Справжні тут — HTTP-стик і межа «API ↔ воркер». Черга і сховище поки заглушки:
// черга в пам'яті й Map замість брокера й бази. Їхня заміна — то вже м'ясо.
const queue: number[] = [];
const store = new Map<string, number>();

// воркер — окрема «частина»: читає з черги й кладе у сховище
setInterval(() => {
  const v = queue.shift();
  if (v !== undefined) store.set("temp", v);      // стик воркер → сховище
}, 50);

http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/temp") {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => { queue.push(Number(body)); res.end("ok"); }); // API → черга
  } else if (req.url === "/temp") {
    res.end(String(store.get("temp") ?? "—"));      // читання: нитка пройшла?
  } else { res.statusCode = 404; res.end(); }
}).listen(8080);
