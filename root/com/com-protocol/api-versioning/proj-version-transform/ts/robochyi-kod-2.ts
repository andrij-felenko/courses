// Запит підіймаємо УПЕРЕД: зміни, випущені ПІСЛЯ версії клієнта,
// від найстарішої до найновішої — доки не отримаємо поточну форму.
function upcast(req: Req, from: string): Req {
  for (const c of changes)
    if (c.version > from && c.upRequest) req = c.upRequest(req);
  return req;
}

// Відповідь опускаємо НАЗАД: той самий набір, але у ЗВОРОТНОМУ порядку,
// від найновішої до найстарішої — доки не дійдемо до версії клієнта.
function downcast(res: Res, to: string): Res {
  for (let i = changes.length - 1; i >= 0; i--) {
    const c = changes[i];
    if (c.version > to && c.downResponse) res = c.downResponse(res);
  }
  return res;
}

// Увесь прохід: версія клієнта → підняти → ядро → опустити → назад клієнтові.
function handle(clientVersion: string, params: Record<string, string>, body: any): Res {
  const coreReq = upcast({ params, body }, clientVersion);
  const coreRes = core(coreReq);          // ядро говорить ЛИШЕ поточною
  return downcast(coreRes, clientVersion);
}

// Ядро знає тільки сьогоднішню форму: total у центах.
function core(r: Req): Res {
  return { status: 200, body: { id: "or_42", total: r.body.total } };
}

// Клієнт, прив'язаний до 2023-05-10, шле стару форму й чекає стару назад:
handle("2023-05-10", {}, { amount: 500 });
// → { status: 200, body: { id: "or_42", amount: 500 } }
