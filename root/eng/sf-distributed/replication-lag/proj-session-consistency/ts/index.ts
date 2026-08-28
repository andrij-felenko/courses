// Клієнтський перехоплювач для браузерних SPA-додатків (TypeScript / Browser)
// Синхронізація LSN між різними вкладками браузера через BroadcastChannel API

export class SessionConsistentClient {
  private minLsn: bigint = 0n;
  private readonly channel: BroadcastChannel;
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.channel = new BroadcastChannel("session_lsn_sync");

    // Отримання свіжих LSN від інших відкритих вкладок того самого користувача
    this.channel.onmessage = (event: MessageEvent<{ minLsn: string }>) => {
      const incomingLsn = BigInt(event.data.minLsn);
      if (incomingLsn > this.minLsn) {
        this.minLsn = incomingLsn;
      }
    };
  }

  // Виконання мутації (POST / PUT / DELETE)
  async write(endpoint: string, body: unknown): Promise<unknown> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-Min-LSN": this.minLsn.toString(),
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Write failed with status ${response.status}`);
    }

    // Отримання нового LSN після фіксації на Primary
    const commitLsnHeader = response.headers.get("X-Session-Min-LSN");
    if (commitLsnHeader) {
      const commitLsn = BigInt(commitLsnHeader);
      this.updateLsn(commitLsn);
    }

    return response.json();
  }

  // Виконання читання (GET) із гарантією Read-Your-Writes та Monotonic Reads
  async read<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: "GET",
      headers: {
        "X-Session-Min-LSN": this.minLsn.toString(),
      },
    });

    if (!response.ok) {
      throw new Error(`Read failed with status ${response.status}`);
    }

    // Оновлення LSN за даними репліки
    const replicaLsnHeader = response.headers.get("X-Session-Min-LSN");
    if (replicaLsnHeader) {
      const replicaLsn = BigInt(replicaLsnHeader);
      this.updateLsn(replicaLsn);
    }

    return response.json() as Promise<T>;
  }

  private updateLsn(newLsn: bigint): void {
    if (newLsn > this.minLsn) {
      this.minLsn = newLsn;
      // Оповіщення інших вкладок про просування монотонного часу
      this.channel.postMessage({ minLsn: newLsn.toString() });
    }
  }
}
