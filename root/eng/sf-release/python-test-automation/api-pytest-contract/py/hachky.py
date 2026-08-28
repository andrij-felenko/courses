@pytest.fixture
def device(port, request):
    reset(port)
    wait_ready(port, timeout=3.0)
    yield Device(port)

    report = request.node.stash.get(phase_report_key, {})
    failed = ("call" not in report) or report["call"].failed
    if failed:
        dump_logs(port, request.node.nodeid)   # артефакт лише там, де він потрібен
