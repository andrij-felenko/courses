// Синхронний get-or-create: у Node одна нитка, гонитві нізвідки взятися
class LoggerRegistry {
  private loggers = new Map<string, Logger>();

  get(name: string): Logger {
    let lg = this.loggers.get(name);
    if (lg === undefined) {
      lg = new Logger(name);          // між get і set керування нікуди не йде
      this.loggers.set(name, lg);
    }
    return lg;
  }
}
