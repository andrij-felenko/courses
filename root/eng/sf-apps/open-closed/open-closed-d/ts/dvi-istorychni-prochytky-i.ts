class CountingList<T> {
  protected count = 0;
  add(x: T): void        { this.count++; this.store(x); }
  addAll(xs: T[]): void  { for (const x of xs) this.add(x); }  // ← базова реалізація гукає власний add()
}

class LoggingList<T> extends CountingList<T> {
  override add(x: T): void       { this.log(x);       super.add(x); }
  override addAll(xs: T[]): void { this.log("batch"); super.addAll(xs); }  // super.addAll → this.add → знову log(x)
}
