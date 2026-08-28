type OpenCommand = { id: string; action: "open" };

class LockController {
  private handled = new Set<string>();   // id уже виконаних наказів
  private actuations = 0;                // скільки разів реально клацнув замок

  handle(cmd: OpenCommand): void {
    if (this.handled.has(cmd.id)) return;   // повтор тієї самої особи — дубль
    this.handled.add(cmd.id);
    this.actuations += 1;                    // фізичний рух засува
  }

  get physicalOpens(): number {
    return this.actuations;
  }
}

// ── Фітнес-функція: падає в збірці, щойно міру порушено ──
function fitnessLockOpensExactlyOnce(): void {
  // 1) хитка мережа: клієнт повторив ОДИН наказ п'ять разів
  const one = new LockController();
  for (let i = 0; i < 5; i++) one.handle({ id: "cmd-42", action: "open" });
  if (one.physicalOpens !== 1) {
    throw new Error(
      `«замок рівно раз» порушено: 5 повторів однієї команди → ` +
        `${one.physicalOpens} відмикань, а міра — рівно 1`,
    );
  }

  // 2) три РІЗНІ накази: дедуплікація не сміє глушити справжні команди
  const many = new LockController();
  for (const id of ["cmd-43", "cmd-44", "cmd-45"]) {
    many.handle({ id, action: "open" });
  }
  if (many.physicalOpens !== 3) {
    throw new Error(
      `«замок рівно раз» порушено: 3 різні команди → ` +
        `${many.physicalOpens} відмикань, а мало бути 3`,
    );
  }
}
