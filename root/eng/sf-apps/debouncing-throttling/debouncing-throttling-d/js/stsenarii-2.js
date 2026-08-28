class DraggableCard {
  constructor(element) {
    this.element = element;
    this.currentX = 0;
    this.currentY = 0;
    this.initEvents();
  }

  updateTransform = rafThrottle((x, y) => {
    this.element.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  });

  onPointerMove = (event) => {
    this.currentX += event.movementX;
    this.currentY += event.movementY;
    this.updateTransform(this.currentX, this.currentY);
  };

  initEvents() {
    this.element.addEventListener('pointermove', this.onPointerMove);
  }

  destroy() {
    this.updateTransform.cancel();
    this.element.removeEventListener('pointermove', this.onPointerMove);
  }
}
