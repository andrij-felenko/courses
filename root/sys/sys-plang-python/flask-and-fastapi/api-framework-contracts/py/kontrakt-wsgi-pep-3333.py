from collections.abc import Callable, Iterable

def application(
    environ: dict[str, object],
    start_response: Callable[
        [str, list[tuple[str, str]], tuple | None],
        Callable[[bytes], None]
    ]
) -> Iterable[bytes]:
    ...
