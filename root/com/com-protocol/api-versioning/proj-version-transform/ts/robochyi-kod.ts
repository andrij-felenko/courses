// Ядро розуміє лише СЬОГОДНІШНЮ форму; будь-які старі форми живуть на краях.
type Req = { params: Record<string, string>; body: any };
type Res = { status: number; body: any };

interface VersionChange {
  version: string;               // дата, коли зміна набула чинності (ISO)
  description: string;
  upRequest?(r: Req): Req;       // форма ДО → форма ПІСЛЯ  (підіймаємо запит)
  downResponse?(r: Res): Res;    // форма ПІСЛЯ → форма ДО  (опускаємо відповідь)
}

// Реєстр змін, відсортований від НАЙСТАРІШОЇ до найновішої.
const changes: VersionChange[] = [
  {
    version: "2024-02-20",
    description: "поле amount перейменовано на total",
    upRequest(r) {
      if (r.body && "amount" in r.body) { r.body.total = r.body.amount; delete r.body.amount; }
      return r;
    },
    downResponse(r) {
      if (r.body && "total" in r.body) { r.body.amount = r.body.total; delete r.body.total; }
      return r;
    },
  },
  {
    version: "2024-11-05",
    description: "суму переведено з доларів у центи",
    upRequest(r) {
      if (r.body && typeof r.body.total === "number") r.body.total *= 100;
      return r;
    },
    downResponse(r) {
      if (r.body && typeof r.body.total === "number") r.body.total = Math.round(r.body.total / 100);
      return r;
    },
  },
];
