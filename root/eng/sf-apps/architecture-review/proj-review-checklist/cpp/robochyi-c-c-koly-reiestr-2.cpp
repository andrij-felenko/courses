static const std::vector<ArchFinding> may_findings = {
    { "стоп на повному ході → мотор стоїть за < 200 мс",
      "стоп у спільній черзі з телеметрією; під піком спізнюється",
      FindingKind::Risk, "Оля", FindingState::Mitigating, 14 },

    { "новий тип давача додається без правки ядра керування",
      "тип давача зашитий у 6 місцях замість одного",
      FindingKind::Risk, "Тарас", FindingState::Open, 30 },

    { "стоп на повному ході → мотор стоїть за < 200 мс",
      "апаратне переривання поза чергою — 200 мс тримаються завжди",
      FindingKind::NonRisk, "Оля", FindingState::Closed, 0 },

    { "синхронна копія журналу в друге сховище",
      "піднімає надійність, опускає латентність запису на ~30 мс",
      FindingKind::Tradeoff, "", FindingState::Open, 0 },   // ← навмисна діра: компроміс без власника
};

static const ArchReviewSession may_review = {
    .system      = "контролер приводу v2",
    .review_day  = 3,
    .facilitator = "Ігор",
    .findings    = may_findings,
};
