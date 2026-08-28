interface Fetcher {
  fetch(input: RequestInfo, init?: RequestInit): Promise<Response>;
}

// Прямий виклик типізованого RPC-інтерфейсу суміжного воркера
interface AuthService {
  validateSession(token: string): Promise<{ userId: string; role: string }>;
  revokeToken(token: string): Promise<boolean>;
}

interface Env {
  AUTH_WORKER: Fetcher & AuthService;
}
