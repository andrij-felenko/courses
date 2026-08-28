class OrderGateway {
  // ⚠️ додали предметне правило В шлюз — і це вже не шлюз
  canCancel(): boolean {
    return this.status === "new" || this.status === "paid";
  }

  cancel(): void {
    if (!this.canCancel())
      throw new Error(`замовлення в статусі ${this.status} не скасувати`);
    this.status = "cancelled";
    this.save();
  }
}
