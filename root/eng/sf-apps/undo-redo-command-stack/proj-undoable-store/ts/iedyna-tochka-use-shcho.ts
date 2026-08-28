  begin(label: string, mergeKey = ""): void {
    if (this.open) throw new Error("вкладені транзакції заборонені: намір не буває всередині наміру");
    this.open = { base: this.root, selBefore: this.sel, label, mergeKey,
                  born0: born, removed: 0, dropped: [], added: [] };
  }

  // Уся модель міняється ТІЛЬКИ тут.
  apply(edit: Edit, selAfter: Selection): void {
    const implicit = !this.open;
    if (implicit) this.begin("зміна");
    try {
      const r = edit(this.root);       // ← усе, що здатне кинути, кидає ТУТ
      this.root = r.root;              // ← присвоєння посилання: не кине ніколи
      this.sel = selAfter;
      this.open!.removed += r.removed;
      this.open!.dropped.push(...r.dropped);
      this.open!.added.push(...r.added);
    } catch (e) {
      this.rollback();
      throw e;
    }
    this.notify();
    if (implicit) this.commit();
  }

  rollback(): void {
    if (!this.open) return;
    this.root = this.open.base;        // одне присвоєння — усе побудоване стає сміттям
    this.sel = this.open.selBefore;
    this.open = null;
    this.notify();
  }
