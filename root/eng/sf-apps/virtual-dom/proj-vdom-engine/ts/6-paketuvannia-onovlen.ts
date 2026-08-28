type RenderCallback = () => void;

class RenderScheduler {
  private queue = new Set<RenderCallback>();
  private isScheduled = false;

  schedule(callback: RenderCallback): void {
    this.queue.add(callback);

    if (!this.isScheduled) {
      this.isScheduled = true;
      queueMicrotask(() => this.flush());
    }
  }

  private flush(): void {
    for (const callback of this.queue) {
      callback();
    }
    this.queue.clear();
    this.isScheduled = false;
  }
}

export const scheduler = new RenderScheduler();
