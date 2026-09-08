import * as net from "node:net";
import { execSync } from "node:child_process";

export interface DatabaseContainerConfig {
  image?: string;
  hostPort?: number;
  database?: string;
  user?: string;
  password?: string;
  timeoutMs?: number;
  forceSimulation?: boolean;
}

export interface RunningContainerInfo {
  containerId: string;
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
  isSimulated: boolean;
}

/**
 * Оркестратор ефемерних інфраструктурних контейнерів для ізольованого тестування приймання.
 * Забезпечує детермінований запуск, верифікацію готовності порту та обов'язковий teardown ресурсів.
 */
export class ContainerOrchestrator {
  private activeContainers: Set<string> = new Set();
  private teardownRegistered = false;

  constructor() {
    this.registerProcessTeardown();
  }

  /**
   * Запускає ефемерний контейнер PostgreSQL та очікує відкриття мережевого порту.
   */
  public async startPostgres(config: DatabaseContainerConfig = {}): Promise<RunningContainerInfo> {
    const image = config.image ?? "postgres:15-alpine";
    const port = config.hostPort ?? 54329;
    const database = config.database ?? "clean_slate_db";
    const user = config.user ?? "acceptance_tester";
    const password = config.password ?? "secret_handover_pwd";
    const timeoutMs = config.timeoutMs ?? 15000;

    const containerName = `handover-pg-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    const isDockerAvailable = !config.forceSimulation && this.checkDockerAvailability();

    if (!isDockerAvailable) {
      // Якщо Docker відсутній або вимкнений, працюємо у контрольованому режимі емуляції
      const simulatedId = `simulated-${containerName}`;
      this.activeContainers.add(simulatedId);
      return {
        containerId: simulatedId,
        host: "127.0.0.1",
        port,
        database,
        user,
        password,
        isSimulated: true,
      };
    }

    const dockerCmd = [
      "docker run -d --rm",
      `--name ${containerName}`,
      `-e POSTGRES_DB=${database}`,
      `-e POSTGRES_USER=${user}`,
      `-e POSTGRES_PASSWORD=${password}`,
      `-p ${port}:5432`,
      image,
    ].join(" ");

    try {
      const containerId = execSync(dockerCmd, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
      this.activeContainers.add(containerId);

      await this.waitForSocketReady("127.0.0.1", port, timeoutMs);

      return {
        containerId,
        host: "127.0.0.1",
        port,
        database,
        user,
        password,
        isSimulated: false,
      };
    } catch (err) {
      this.stop(containerName);
      throw new Error(`Помилка запуску ефемерного контейнера: ${err instanceof Error ? err.message : String(err)}`);
    }
  }

  /**
   * Зупиняє і примусово видаляє запущений контейнер.
   */
  public stop(containerId: string): void {
    if (!containerId) return;

    if (containerId.startsWith("simulated-")) {
      this.activeContainers.delete(containerId);
      return;
    }

    try {
      execSync(`docker rm -f ${containerId}`, { stdio: "ignore" });
    } catch {
      // Ігноруємо помилки, якщо контейнер уже зупинено
    } finally {
      this.activeContainers.delete(containerId);
    }
  }

  /**
   * Гарантоване очищення всіх зареєстрованих ефемерних контейнерів.
   */
  public stopAll(): void {
    for (const id of Array.from(this.activeContainers)) {
      this.stop(id);
    }
  }

  private waitForSocketReady(host: string, port: number, timeoutMs: number): Promise<void> {
    const startTime = Date.now();

    return new Promise((resolve, reject) => {
      const tryConnect = () => {
        if (Date.now() - startTime >= timeoutMs) {
          reject(new Error(`Таймаут очікування порту ${host}:${port} (${timeoutMs}мс)`));
          return;
        }

        const socket = new net.Socket();
        socket.setTimeout(1000);

        socket.on("connect", () => {
          socket.destroy();
          resolve();
        });

        socket.on("error", () => {
          socket.destroy();
          setTimeout(tryConnect, 300);
        });

        socket.on("timeout", () => {
          socket.destroy();
          setTimeout(tryConnect, 300);
        });

        socket.connect(port, host);
      };

      tryConnect();
    });
  }

  private checkDockerAvailability(): boolean {
    try {
      execSync("docker info", { stdio: "ignore" });
      return true;
    } catch {
      return false;
    }
  }

  private registerProcessTeardown(): void {
    if (this.teardownRegistered) return;
    this.teardownRegistered = true;

    const cleanup = () => {
      if (this.activeContainers.size > 0) {
        this.stopAll();
      }
    };

    process.on("exit", cleanup);
    process.on("SIGINT", () => {
      cleanup();
      process.exit(130);
    });
    process.on("SIGTERM", () => {
      cleanup();
      process.exit(143);
    });
  }
}
