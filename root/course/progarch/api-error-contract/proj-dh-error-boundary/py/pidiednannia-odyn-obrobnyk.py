import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def install_error_boundary(app: FastAPI, expose_internals: bool) -> None:
    @app.exception_handler(Exception)            # ловить УСЕ, що долетіло до краю
    async def _boundary(request: Request, err: Exception):
        req_id = getattr(request.state, "req_id", None) \
            or request.headers.get("X-Request-Id") or str(uuid.uuid4())
        status, headers, body = to_problem(err, req_id, expose_internals)
        headers.pop("Content-Type", None)        # media_type виставить його сам
        headers["X-Request-Id"] = req_id
        return JSONResponse(status_code=status, content=body,
                            media_type="application/problem+json", headers=headers)

# install_error_boundary(app, expose_internals=settings.env != "production")
