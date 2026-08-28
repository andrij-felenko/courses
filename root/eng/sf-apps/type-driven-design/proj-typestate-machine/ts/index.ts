type Closed = "closed";
type Open   = "open";
type Authed = "authed";

class Wire {
    private constructor(private readonly peer: string) {}
    static dial(peer: string): Wire { return new Wire(peer); }
    put(bytes: string): void { /* запис у канал */ }
    roundtrip(body: string): Uint8Array { this.put(body); return new Uint8Array(); }
}

class Conn<S extends Closed | Open | Authed> {
    // Фантомне поле: несе стан S у ТИПІ. `declare` — у рантаймі поля немає.
    private declare readonly _state: S;
    private constructor(private readonly wire: Wire) {}

    static start(peer: string): Conn<Closed> { return new Conn(Wire.dial(peer)); }

    // `this: Conn<...>` — параметр this: метод доступний лише в цьому стані.
    open(this: Conn<Closed>): Conn<Open> {
        return this as unknown as Conn<Open>;
    }
    authenticate(this: Conn<Open>, key: string): Conn<Authed> {
        this.wire.put(key);
        return this as unknown as Conn<Authed>;   // ТОЙ САМИЙ об'єкт, лише перетипований
    }
    request(this: Conn<Authed>, body: string): Uint8Array {
        return this.wire.roundtrip(body);
    }
    close(this: Conn<Open> | Conn<Authed>): Conn<Closed> {
        return this as unknown as Conn<Closed>;
    }
}
