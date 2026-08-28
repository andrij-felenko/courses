class Device {
  private status: DeviceStatus = "new";        // закрите: ззовні не дотягтися
  private homeId: HomeId | null = null;

  commission(homeId: HomeId): void {
    if (this.status !== "new")
      throw new DomainError("пристрій уже введено в дім");
    this.status = "online";
    this.homeId = homeId;
  }

  markOffline(): void {
    if (this.status === "offline") return;      // уже мовчить — тихий no-op
    if (this.status !== "online")
      throw new DomainError("мовчати може лише пристрій, що був на зв'язку");
    this.status = "offline";
  }

  markOnline(): void {
    if (this.status === "online") return;        // уже на зв'язку
    if (this.status !== "offline")
      throw new DomainError("на зв'язок вертається лише offline-пристрій");
    this.status = "online";
  }

  retire(): void {
    if (this.status === "retired") return;       // ідемпотентно
    if (this.status === "new")
      throw new DomainError("ще не введений пристрій не списують");
    this.status = "retired";                      // з online чи offline — назавжди
  }
}
