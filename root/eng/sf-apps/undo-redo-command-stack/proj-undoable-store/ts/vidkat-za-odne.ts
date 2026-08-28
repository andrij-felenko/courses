  private pushStep(st: Step): void {
    // 1. Зріз гілки повтору
    while (this.steps.length > this.index) {
      const cut = this.steps.pop()!;
      this.bytes -= cut.weight;
      this.retire(cut, "top");          // гине after зрізаних кроків → звільняється ДОДАНЕ
    }
    if (this.saved > this.index) this.saved = -1;   // точка збереження була в зрізаному

    // 2. Новий крок
    this.bytes += st.weight;
    this.steps.push(st);
    this.index++;

    // 3. Бюджет
    this.trim();
  }

  undo(): boolean {
    if (this.open || this.index === 0) return false;
    const s = this.steps[this.index - 1];
    this.root = s.before;               // ← весь відкат: одне присвоєння посилання
    this.sel = s.selBefore;
    this.index--;
    this.notify();
    return true;
  }

  redo(): boolean {
    if (this.open || this.index >= this.steps.length) return false;
    const s = this.steps[this.index];
    this.root = s.after;
    this.sel = s.selAfter;
    this.index++;
    this.notify();
    return true;
  }
