class EntityStateHolder {
  private latestSeq = 0;
  private value = false;

  public applyServerResponse(seq: number, serverValue: boolean) {
    // Якщо прийшла відповідь на старіший запит, ніж той, що ми вже врахували — відкидаємо
    if (seq < this.latestSeq) {
      console.warn(`Застаріла відповідь seq=${seq} проігнорована (поточна seq=${this.latestSeq})`);
      return;
    }
    this.latestSeq = seq;
    this.value = serverValue;
  }
}
