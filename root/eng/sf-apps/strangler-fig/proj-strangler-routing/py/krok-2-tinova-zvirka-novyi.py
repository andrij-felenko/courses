from dataclasses import dataclass
import json

@dataclass
class Diff:
    path: str
    status: str              # "match" | "mismatch" | "error"
    details: str | None = None

# record_diff(d: Diff) -> None   → метрика/лог розбіжностей

def canonical(v) -> str:
    """Канонічний вигляд значення: ключі за абеткою, стабільний порядок —
    інакше {'a':1,'b':2} і {'b':2,'a':1} здалися б різними."""
    return json.dumps(v, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)

def bodies_equal(a, b) -> bool:
    # НЕ «==» по сирих відповідях: у них повно полів, що законно різняться
    # (час генерації, порядок ключів). Звіряємо лише СУТЬ, нормалізувавши обидві.
    return canonical(a) == canonical(b)


async def read_with_shadow(rule: RouteRule, req) -> "Response":
    """Читання з тінню. Клієнт ЗАВЖДИ отримує результат контролю (старе)."""
    path = req.path
    control = await call_legacy(req)            # старе — його й віддамо

    if rule.shadow:
        # кандидат виконуємо, але його падіння НЕ сміє зачепити клієнта
        try:
            candidate = await call_service(rule.service_url, req)
            a = control.json()
            b = candidate.json()
            same = bodies_equal(a, b)
            record_diff(Diff(path,
                "match" if same else "mismatch",
                None if same else f"control={a!r} candidate={b!r}"))
        except Exception as e:
            # кандидат упав або відповів не-JSON — це теж цінний сигнал
            record_diff(Diff(path, "error", str(e)))
    return control                              # клієнтові — тільки старе
