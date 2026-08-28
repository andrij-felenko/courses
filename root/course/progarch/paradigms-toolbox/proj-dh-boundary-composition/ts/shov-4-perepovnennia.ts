private static readonly CAP = 64;
private dropped = 0;

post(f: Frame): void {
  if (this.mailbox.length >= DeviceActor.CAP) {
    this.mailbox.shift();     // політика для СТАНУ: викинь найстаріший (dropHead) = конфляція
    this.dropped++;           // але порахуй викинуте — німа втрата гірша за гучну
  }
  this.mailbox.push(f);
  if (!this.draining) { this.draining = true; setImmediate(() => this.drain()); }
}
