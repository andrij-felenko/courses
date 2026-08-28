// пакет boundary. Домен — три речі, що течуть крізь межу.
type Command = { key: string; kind: string; dev: string; arg?: string }; // key = ключ ідемпотентності
type Result  = { ok: boolean; note: string };
type Report  = { dev: string; field: string; value: string; ts: number }; // ts = ВЛАСНА мітка відліку

// Порт, що бачить логіка хаба (та сама форма, що в статті).
interface CloudLink {
  send(cmd: Command): Promise<Result>; // команда: синхронно, «фактично раз»
  emit(rep: Report): void;             // звіт: у буфер і назад, не чекаючи мережі
}

// Те, що фізично лягає в мережу. НЕнадійне: таймаут, обрив, тиша.
interface Wire {
  postCmd(cmd: Command, signal?: AbortSignal): Promise<Result>;
  postReport(rep: Report, signal?: AbortSignal): Promise<void>;
  getState(dev: string, signal?: AbortSignal): Promise<string>;
}
class Unreachable extends Error {} // справжній Wire перекладає сюди обрив/таймаут fetch
