interface Account { balance: number }
const EMPTY: Account = { balance: 0 };

// apply — СЛІПА: приймає народжену подію на віру, правил не знає.
function apply(state: Account, e: AccountEvent): Account {
  switch (e.kind) {
    case "Deposited":  return { balance: state.balance + e.amount };
    case "Withdrawn":  return { balance: state.balance - e.amount };
    case "FeeCharged": return { balance: state.balance - e.amount };
  }
}

// Згорнути список збережених подій у стан.
function foldState(events: Stored[]): Account {
  return events.reduce((s, st) => apply(s, st.event), EMPTY);
}

// Команда «зняти»: правила ТУТ. Повертаємо, чи вдалося (для повтору при конфлікті).
function withdraw(store: EventStore, streamId: string, amount: number): boolean {
  const history = store.read(streamId);
  const state = foldState(history);            // стан, на якому будуємо рішення
  const expectedVersion = history.length;      // версія, яку ми бачили

  if (amount <= 0) throw new Error("сума має бути додатна");
  if (amount > state.balance) return false;    // ПРАВИЛО: не даємо піти в мінус

  const event: AccountEvent = { kind: "Withdrawn", amount };
  try {
    store.append(streamId, expectedVersion, [event]);
    return true;
  } catch (e) {
    if (e instanceof VersionConflict) return false;  // хтось випередив — хай виклик повторить
    throw e;
  }
}
