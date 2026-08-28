may_findings = [
    ArchFinding("стоп на повному ході → мотор стоїть за < 200 мс",
                "стоп у спільній черзі з телеметрією; під піком спізнюється",
                FindingKind.RISK, "Оля", FindingState.MITIGATING, 14),

    ArchFinding("новий тип давача додається без правки ядра керування",
                "тип давача зашитий у 6 місцях замість одного",
                FindingKind.RISK, "Тарас", FindingState.OPEN, 30),

    ArchFinding("стоп на повному ході → мотор стоїть за < 200 мс",
                "апаратне переривання поза чергою — 200 мс тримаються завжди",
                FindingKind.NON_RISK, "Оля", FindingState.CLOSED, 0),

    ArchFinding("синхронна копія журналу в друге сховище",
                "піднімає надійність, опускає латентність запису на ~30 мс",
                FindingKind.TRADEOFF, None, FindingState.OPEN, 0),   # ← навмисна діра: компроміс без власника
]

may_review = ArchReviewSession(
    system="контролер приводу v2",
    review_day=3,
    facilitator="Ігор",
    findings=may_findings,
)
