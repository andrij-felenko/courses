class OrderDialog implements Mediator {           // КОНКРЕТНИЙ ПОСЕРЕДНИК
  readonly selfPickup = new Checkbox(this);       // тримає всіх колег
  readonly address    = new TextField(this);
  readonly submit     = new Button(this);

  notify(sender: Widget, event: string) {         // уся логіка вікна — тут
    if (sender === this.selfPickup && event === "toggled") {
      this.address.enabled = !this.selfPickup.checked;   // самовивіз → адреса зайва
      if (this.selfPickup.checked) this.address.value = "";
    }
    // кнопка активна, якщо самовивіз АБО адресу вписано
    this.submit.enabled = this.selfPickup.checked || this.address.value.trim() !== "";
    this.submit.render();
  }
}
