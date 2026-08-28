// TypeScript: Повнофункціональний веб-віртуалізатор з ResizeObserver та Scroll Anchoring

export interface VirtualItem {
  index: number;
  offset: number;
  size: number;
}

export interface VirtualizerOptions {
  count: number;
  estimateSize: (index: number) => number;
  overscan?: number;
  scrollerElement: HTMLElement;
  contentElement: HTMLElement;
}

export class DynamicVirtualizer {
  private count: number;
  private estimateSize: (index: number) => number;
  private overscan: number;
  private scroller: HTMLElement;
  private content: HTMLElement;

  private measuredSizes: Map<number, number> = new Map();
  private offsets: number[] = [];
  private totalHeight: number = 0;

  private resizeObserver: ResizeObserver;
  private pendingMeasurements: Map<number, number> = new Map();
  private isRafScheduled: boolean = false;

  constructor(options: VirtualizerOptions) {
    this.count = options.count;
    this.estimateSize = options.estimateSize;
    this.overscan = options.overscan ?? 3;
    this.scroller = options.scrollerElement;
    this.content = options.contentElement;

    this.recomputeOffsets();

    this.resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const target = entry.target as HTMLElement;
        const indexAttr = target.getAttribute('data-index');
        if (indexAttr !== null) {
          const index = parseInt(indexAttr, 10);
          const height = entry.borderBoxSize?.[0]?.blockSize ?? target.offsetHeight;
          if (height > 0 && this.measuredSizes.get(index) !== height) {
            this.pendingMeasurements.set(index, height);
          }
        }
      }
      this.scheduleMeasurementFlush();
    });

    this.scroller.addEventListener('scroll', () => this.render(), { passive: true });
    this.render();
  }

  private recomputeOffsets(): void {
    this.offsets = new Array(this.count + 1);
    this.offsets[0] = 0;
    for (let i = 0; i < this.count; i++) {
      const h = this.measuredSizes.get(i) ?? this.estimateSize(i);
      this.offsets[i + 1] = this.offsets[i] + h;
    }
    this.totalHeight = this.offsets[this.count];
    this.content.style.height = `${this.totalHeight}px`;
  }

  // Двійковий пошук першого елемента, чиє закінчення > scrollTop
  private findStartIndex(scrollTop: number): number {
    let low = 0;
    let high = this.count - 1;
    let result = 0;

    while (low <= high) {
      const mid = (low + high) >>> 1;
      if (this.offsets[mid + 1] > scrollTop) {
        result = mid;
        high = mid - 1;
      } else {
        low = mid + 1;
      }
    }
    return result;
  }

  public getRange(scrollTop: number, viewportHeight: number): { start: number; end: number } {
    if (this.count === 0) return { start: 0, end: 0 };

    const firstVisible = this.findStartIndex(scrollTop);
    let lastVisible = firstVisible;

    while (lastVisible < this.count - 1 && this.offsets[lastVisible] < scrollTop + viewportHeight) {
      lastVisible++;
    }

    const start = Math.max(0, firstVisible - this.overscan);
    const end = Math.min(this.count - 1, lastVisible + this.overscan);

    return { start, end };
  }

  private scheduleMeasurementFlush(): void {
    if (this.isRafScheduled || this.pendingMeasurements.size === 0) return;
    this.isRafScheduled = true;

    requestAnimationFrame(() => {
      this.isRafScheduled = false;
      this.flushMeasurements();
    });
  }

  private flushMeasurements(): void {
    if (this.pendingMeasurements.size === 0) return;

    // Фіксуємо якірний елемент та його положення до оновлення префіксних сум
    const currentScrollTop = this.scroller.scrollTop;
    const anchorIndex = this.findStartIndex(currentScrollTop);
    const oldAnchorOffset = this.offsets[anchorIndex];

    // Застосовуємо нові заміри
    for (const [index, height] of this.pendingMeasurements.entries()) {
      this.measuredSizes.set(index, height);
    }
    this.pendingMeasurements.clear();

    this.recomputeOffsets();

    // Scroll Anchoring: якщо висоти елементів над якорем змінилися — компенсуємо scrollTop
    const newAnchorOffset = this.offsets[anchorIndex];
    const scrollDelta = newAnchorOffset - oldAnchorOffset;

    if (scrollDelta !== 0) {
      this.scroller.scrollTop = currentScrollTop + scrollDelta;
    }

    this.render();
  }

  public render(): void {
    const scrollTop = this.scroller.scrollTop;
    const viewportHeight = this.scroller.clientHeight;
    const { start, end } = this.getRange(scrollTop, viewportHeight);

    // Збір існуючих вузлів у DOM
    const existingNodes = new Map<number, HTMLElement>();
    for (let i = 0; i < this.content.children.length; i++) {
      const child = this.content.children[i] as HTMLElement;
      const idx = parseInt(child.getAttribute('data-index') ?? '-1', 10);
      if (idx >= 0) existingNodes.set(idx, child);
    }

    // Рендеринг активного вікна
    const activeIndices = new Set<number>();
    for (let i = start; i <= end; i++) {
      activeIndices.add(i);
      let node = existingNodes.get(i);

      if (!node) {
        node = document.createElement('div');
        node.className = 'virtual-item';
        node.setAttribute('data-index', i.toString());
        node.style.position = 'absolute';
        node.style.top = '0';
        node.style.left = '0';
        node.style.width = '100%';
        node.textContent = `Запис #${i} (висота: ${this.measuredSizes.get(i) ?? 'очікується'})`;
        
        this.content.appendChild(node);
        this.resizeObserver.observe(node);
      }

      // Позиціонування через апаратне зміщення без тригера Layout
      const itemTop = this.offsets[i];
      node.style.transform = `translateY(${itemTop}px)`;
    }

    // Видалення / ресайклінг вузлів, що вийшли за межі буфера
    for (const [idx, node] of existingNodes.entries()) {
      if (!activeIndices.has(idx)) {
        this.resizeObserver.unobserve(node);
        node.remove();
      }
    }
  }

  public destroy(): void {
    this.resizeObserver.disconnect();
  }
}
