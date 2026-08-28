// ── 1. Об'єкти-значення: незмінні, рівність за вмістом, стережуть себе ──
class DomainError extends Error {}

class DeviceId {
  constructor(readonly value: string) {
    if (!value) throw new DomainError("порожній DeviceId — ідентифікатор мусить бути");
  }
  equals(o: DeviceId): boolean { return this.value === o.value; }
  toString(): string { return this.value; }
}
class HomeId { constructor(readonly value: string) {} toString() { return this.value; } }
class RoomId { constructor(readonly value: string) {} toString() { return this.value; } }
class UserId { constructor(readonly value: string) {} toString() { return this.value; } }

// Замкнені переліки — інших значень не буває. Unknown/невизначеність — чесний стан, не null.
type LockState = "Locked" | "Unlocked" | "Jammed" | "Unknown";
type HomeMode  = "Home" | "Away" | "Night";

class Threshold { constructor(readonly celsius: number) {} }

// Вимір — значення: незмінний, два однакові взаємозамінні.
class Reading {
  constructor(readonly celsius: number, readonly at: Date) {}
  hotterThan(t: Threshold): boolean { return this.celsius > t.celsius; }
}

// Локація — де саме стоїть пристрій (кімната + місце); теж значення.
class Location {
  constructor(readonly roomId: RoomId, readonly spot: string) {}
}
