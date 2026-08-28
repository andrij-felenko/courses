# FastAPI: та сама позначка як залежність
from datetime import datetime, timezone

def deprecate(announced: str, sunset: str, docs: str):
    a = datetime.fromisoformat(announced).replace(tzinfo=timezone.utc)
    s = datetime.fromisoformat(sunset).replace(tzinfo=timezone.utc)
    def stamp(response: Response):
        response.headers["Deprecation"] = f"@{int(a.timestamp())}"
        response.headers["Sunset"] = s.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response.headers["Link"] = f'<{docs}>; rel="deprecation"; type="text/html"'
    return stamp

@app.get("/v1/orders",
         dependencies=[Depends(deprecate("2024-06-30", "2025-12-31", DOCS))])
def list_orders_v1(): ...
