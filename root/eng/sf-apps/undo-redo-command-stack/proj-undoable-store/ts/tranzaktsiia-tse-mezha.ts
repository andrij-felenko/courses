  commit(): void {
    if (!this.open) return;
    const op = this.open;
    this.open = null;
    if (this.root === op.base) return;               // нічого не змінилося — кроку не буде

    const w = (born - op.born0) + op.removed;        // додане + вилучене
    const now = performance.now();

    const canMerge =
      op.mergeKey !== "" &&
      this.index === this.steps.length &&            // ми на кінці лінії
      this.index > 0 &&
      this.steps[this.index - 1].mergeKey === op.mergeKey &&
      now - this.steps[this.index - 1].at < 700 &&
      this.saved !== this.index;                     // ← на цьому кроці стоїть точка збереження

    if (canMerge) {
      const last = this.steps[this.index - 1];
      last.after = this.root; last.selAfter = this.sel;
      last.weight += w; last.at = now;
      last.dropped.push(...op.dropped); last.added.push(...op.added);
      this.bytes += w;
      this.trim();
      return;
    }
    this.pushStep({ before: op.base, after: this.root,
                    selBefore: op.selBefore, selAfter: this.sel,
                    label: op.label, mergeKey: op.mergeKey, weight: w,
                    dropped: op.dropped, added: op.added, at: now });
  }

  // Межа наміру як область видимості: те саме, що робить деструктор у C++, тут робить finally.
  transact<T>(label: string, body: () => T, mergeKey = ""): T {
    this.begin(label, mergeKey);
    let ok = false;
    try { const out = body(); ok = true; this.commit(); return out; }
    finally { if (!ok) this.rollback(); }
  }
