const BASIC = new Set(["export-csv"]);   // що дозволено на вільному тарифі

interface Subscription {
  price(): number;
  storageGb(): number;
  seats(): number;
  includes(feature: string): boolean;
}

class Account {
  constructor(
    readonly name: string,
    private sub: Subscription | null,    // вільні користувачі: null
  ) {}

  monthlyPrice(): number {
    if (this.sub !== null) return this.sub.price();
    return 0;                            // вільний тариф
  }
  storageGb(): number {
    if (this.sub !== null) return this.sub.storageGb();
    return 1;                            // вільний тариф: 1 ГБ
  }
  seats(): number {
    if (this.sub !== null) return this.sub.seats();
    return 1;
  }
  hasFeature(f: string): boolean {
    if (this.sub !== null) return this.sub.includes(f);
    return BASIC.has(f);
  }
}
