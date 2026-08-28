const LAG_WINDOW_MS = 3000;   // консервативна стеля очікуваного лагу реплік

type ReadKind = "lock" | "device_state" | "registry" | "telemetry";

class ReadRouter {
  private lastWrite = new Map<string, number>();      // home_id → час останнього запису сесії
  constructor(private leader: Node, private followers: Node[]) {}

  noteWrite(homeId: string): void {                   // застосунок щойно записав у твін на лідері
    this.lastWrite.set(homeId, performance.now());
  }

  route(homeId: string, kind: ReadKind): Node {
    if (kind === "lock") return this.leader;          // безпека: стан замка завжди з лідера
    if (kind === "device_state") {
      const wrote = this.lastWrite.get(homeId) ?? -Infinity;
      if (performance.now() - wrote < LAG_WINDOW_MS)
        return this.leader;                            // read-your-writes: свій свіжий запис
      return this.pickFollower(homeId);                // давній/чужий стан — лаг стерпний
    }
    return this.pickFollower(homeId);                  // реєстр, телеметрія — лаг ок
  }

  private pickFollower(homeId: string): Node {         // монотонні читання: сесія → та сама репліка
    return this.followers[hashString(homeId) % this.followers.length];
  }
}
