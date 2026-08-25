(window.__MODREG__ = window.__MODREG__ || []).push({
  n: 1,
  slug: "audit-framework",
  title: "Підсистема аудиту ядра: правила, події й auditd",
  chapters: [
    {
      n: 1,
      title: "Linux Audit Framework",
      dir: "observability/audit-framework",
      main: "audit-framework-d.md",
      status: "done",
      scope: "Детальна стаття про підсистему аудиту ядра, auditd, auditctl",
      topics: [
        {
          kind: "api",
          file: "api-auditctl-rules.md",
          at: "after",
          status: "done",
          title: "Синтаксис правил auditctl"
        }
      ]
    }
  ]
});
