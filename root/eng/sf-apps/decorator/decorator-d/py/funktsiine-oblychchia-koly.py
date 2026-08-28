# компонент — це функція Handler: Request -> Response
# декоратор — функція Handler -> Handler
def timed(handler):
    def wrapped(req):
        t0 = time.perf_counter()
        resp = handler(req)                    # делегація до вкладеного обробника
        log(f"{req.path}: {(time.perf_counter()-t0)*1e3:.1f} ms")
        return resp
    return wrapped

@timed                                          # @ — це просто home = timed(home)
def home(req):
    return Response("hello")
