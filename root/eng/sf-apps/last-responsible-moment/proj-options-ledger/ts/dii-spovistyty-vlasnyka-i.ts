type Roster = Set<string>;   // хто зараз у команді

interface AdrSupersede { supersedes: string; status: "proposed"; rationale: string; }

// notify — межа інтеграції: канал команди (чат, пошта, тикет). Тут лише виклик.
declare function notify(owner: string, message: string): void;

function act(ev: FireEvent, roster: Roster, fallback: string): AdrSupersede {
  // Пастка «осиротілий власник»: перевіряємо, що власник іще живий.
  const owner = roster.has(ev.owner) ? ev.owner : fallback;
  const orphaned = owner !== ev.owner;

  notify(owner, [
    `Настав відповідальний момент: ${ev.title}.`,
    `Невизначеність знято — час обрати з: ${ev.options.join(", ")}.`,
    orphaned ? `⚠ Початковий власник (${ev.owner}) поза командою — ескальовано на ${owner}.` : "",
  ].filter(Boolean).join(" "));

  return { supersedes: ev.adr, status: "proposed",
           rationale: `Тригер спрацював: ${ev.uncertainty}.` };
}
