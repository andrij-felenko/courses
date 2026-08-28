interface Logger {
  write(msg: string): void;
}

class FileLogger implements Logger {
  constructor(private path: string) {}
  write(msg: string): void {
    appendFileSync(this.path, msg + "\n");
  }
}

class NullLogger implements Logger {
  write(_msg: string): void { /* навмисно нічого */ }
}
