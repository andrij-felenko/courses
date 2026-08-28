# Компактний конструктор: ключ прояву = "<в'ю>:<назва>".
def M(view: View, label: str) -> Manifestation:
    return Manifestation(f"{view}:{label}", view, label)

def build_demo() -> Description:
    return Description(
        manifestations=[
            M("functional", "OrderApi"),    M("functional", "OrderValidator"),
            M("functional", "PricingEngine"), M("functional", "AuditLog"),
            M("development", "order-api"),  M("development", "order-validation"),
            M("development", "pricing"),    M("development", "audit"),
            M("concurrency", "api-loop"),   M("concurrency", "order-pool"),
            M("concurrency", "pricing-pool"),              # ← для AuditLog прояву в конкурентній НЕМАЄ
            M("deployment", "OrderApi"),    M("deployment", "OrderValidator"),
            M("deployment", "PricingEngine"), M("deployment", "AuditLog"),
            M("information", "draft-order"),
        ],
        correspondences=[
            Correspondence("functional:OrderApi", "development:order-api"),
            Correspondence("functional:OrderApi", "concurrency:api-loop"),
            Correspondence("functional:OrderApi", "deployment:OrderApi"),
            Correspondence("functional:OrderValidator", "development:order-validation"),
            Correspondence("functional:OrderValidator", "concurrency:order-pool"),
            Correspondence("functional:OrderValidator", "deployment:OrderValidator"),
            Correspondence("functional:OrderValidator", "information:draft-order"),
            Correspondence("functional:PricingEngine", "development:pricing"),
            Correspondence("functional:PricingEngine", "concurrency:pricing-pool"),
            Correspondence("functional:PricingEngine", "deployment:PricingEngine"),
            Correspondence("functional:AuditLog", "development:audit"),
            Correspondence("functional:AuditLog", "deployment:AuditLog"),  # ← конкурентної немає → сирота
        ],
        deployment=Deployment(
            hosts={
                "deployment:OrderApi": ["svc-api"],
                "deployment:OrderValidator": ["svc-order-1", "svc-order-2"],   # ← репліки!
                "deployment:PricingEngine": ["svc-pricing"],
                "deployment:AuditLog": ["svc-api"],
            },
            links=[
                ("svc-api", "svc-order-1"), ("svc-api", "svc-order-2"),
                ("svc-order-1", "svc-pricing"), ("svc-order-2", "svc-pricing"),
            ],
        ),
        calls=[
            Call("functional:OrderApi", "functional:OrderValidator", "local"),   # ← БАГ
            Call("functional:OrderApi", "functional:AuditLog", "local"),         # ← щиро локальний
            Call("functional:OrderValidator", "functional:PricingEngine", "remote"),
        ],
        required_views=["development", "concurrency", "deployment"],
    )

def run(desc: Description) -> int:
    groups = resolve_groups(desc)
    orphans = check_coverage(groups, desc.required_views)
    false_locals = check_false_local(desc, groups)

    for o in orphans:
        print(f"[orphan]       {o.element} — немає прояву в в'ю: {', '.join(o.missing)}")
    for f in false_locals:
        print(f"[false-local]  {f.frm} → {f.to} — {f.why}")

    total = len(orphans) + len(false_locals)
    print(f"consistency: {total} violation(s)")
    return 0 if total == 0 else 1                       # 0 — пропустити, 1 — завалити збірку

if __name__ == "__main__":
    import sys
    sys.exit(run(build_demo()))
