from typing import Iterator

# Ядро ВИДАЄ описи по одному — весь план не тримається в пам'яті.
def decide_stream(rows: list[Row]) -> Iterator[Effect]:
    for r in rows:
        if r.valid:
            yield Audit(line=f"import {r.id}")

# Оболонка виконує кожен опис одразу, щойно ядро його видало.
async def run_stream(effects: Iterator[Effect]) -> None:
    for e in effects:
        await execute(e)                       # пам'ять — один опис за раз
