class DraggableCard {
  private element: HTMLElement;
  private currentX = 0;
  private currentY = 0;

  constructor(element: HTMLElement) {
    this.element = element;
    this.initEvents();
  }

  private updateTransform = rafThrottle((x: number, y: number) => {
    // Зміна transform виконується на GPU строго перед фазою Paint
    this.element.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  });

  private onPointerMove = (event: PointerEvent): void => {
    this.currentX += event.movementX;
    this.currentY += event.movementY;
    // Викликаємо тротлер: 1000 подій миші коалесціюються в 60/120 викликів на секунду
    this.updateTransform(this.currentX, this.currentY);
  };

  private initEvents(): void {
    this.element.addEventListener('pointermove', this.onPointerMove);
  }

  public destroy(): void {
    this.updateTransform.cancel();
    this.element.removeEventListener('pointermove', this.onPointerMove);
  }
}
