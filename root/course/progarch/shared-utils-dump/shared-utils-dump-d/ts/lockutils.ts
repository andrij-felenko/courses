// Анемічна сутність: пасивний контейнер даних без власної поведінки
export interface SmartLock {
  id: string;
  isLocked: boolean;
  batteryLevel: number;
  tamperAlert: boolean;
}

// Доменні правила вимиті у статичний хелпер спільного пакета
export class LockUtils {
  public static canChangeLockState(lock: SmartLock, batteryThreshold: number): boolean {
    if (lock.tamperAlert) return false;
    return lock.batteryLevel >= batteryThreshold;
  }

  public static unlock(lock: SmartLock): void {
    if (this.canChangeLockState(lock, 15)) {
      lock.isLocked = false;
    }
  }
}
