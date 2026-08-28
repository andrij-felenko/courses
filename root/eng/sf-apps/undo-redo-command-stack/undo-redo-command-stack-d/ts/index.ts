class History {
  private steps: Step[] = [];
  private index = 0;        // скільки кроків застосовано
  private savedIndex = 0;   // індекс, на якому документ збережено

  markSaved(): void { this.savedIndex = this.index; }
  isDirty(): boolean { return this.index !== this.savedIndex; }

  // нова дія зрізає гілку повтору
  push(step: Step): void {
    this.steps.length = this.index;                 // усе після поточного — відрізано
    if (this.savedIndex > this.index) this.savedIndex = -1;  // збереження було в зрізаному
    this.steps.push(step);
    this.index++;
  }
}
