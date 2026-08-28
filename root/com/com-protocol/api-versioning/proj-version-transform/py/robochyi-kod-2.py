def upcast(req: Req, frm: str) -> Req:
    for c in changes:                      # від старих до нових
        if c.version > frm and c.up_request:
            req = c.up_request(req)
    return req

def downcast(res: Res, to: str) -> Res:
    for c in reversed(changes):            # від нових до старих
        if c.version > to and c.down_response:
            res = c.down_response(res)
    return res

def handle(client_version: str, params: dict, body: dict) -> Res:
    core_req = upcast({"params": params, "body": body}, client_version)
    core_res = core(core_req)              # ядро — лише поточна форма
    return downcast(core_res, client_version)

def core(r: Req) -> Res:                    # знає тільки сьогоднішню форму
    return {"status": 200, "body": {"id": "or_42", "total": r["body"]["total"]}}

handle("2023-05-10", {}, {"amount": 500})
# → {"status": 200, "body": {"id": "or_42", "amount": 500}}
