// Багата модель: поліс сам стежить за своїми правилами
class Policy {
  private status: PolicyStatus = PolicyStatus.Active;
  private balance = 0;

  // єдиний спосіб увійти в пільговий період — через це правило
  enterGracePeriod(): void {
    if (this.status !== PolicyStatus.Active)
      throw new DomainError("до пільгового періоду входять лише з активного");
    if (this.balance < 0)
      throw new DomainError("не можна з простроченим внеском");
    this.status = PolicyStatus.GracePeriod;
  }

  isActive(): boolean { return this.status === PolicyStatus.Active; }
}
