import { createServer } from "node:http";

// chain: reduceRight нанизує з кінця — останній шар найглибше, перший найзовні.
function chain(handler: Handler, ...mw: Middleware[]): Handler {
  return mw.reduceRight((next, m) => m(next), handler);
}

const business: Handler = async () => ({
  status: 200,
  headers: { "content-type": "text/plain" },
  body: "привіт зі справжнього обробника",
});
const store = new Map<string, Res>();

const app = chain(business,
  recover, logger, timer, auth, gzip, cache(store), // зовні → всередину
);

createServer(async (nodeReq, nodeRes) => {
  const req: Req = {
    method: nodeReq.method ?? "GET",
    path: nodeReq.url ?? "/",
    headers: nodeReq.headers as Record<string, string>,
  };
  const res = await app(req);
  nodeRes.writeHead(res.status, res.headers);
  nodeRes.end(res.body);
}).listen(8080);
