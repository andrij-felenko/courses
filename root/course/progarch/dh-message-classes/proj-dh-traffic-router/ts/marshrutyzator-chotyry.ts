// ── МАРШРУТИЗАТОР: чотири класи → чотири канали → чотири ДІЄСЛОВА ──
class DHTraffic {
  private readonly deviceQueues = new Map<string, Queue<Command>>();  // адресована черга НА КОЖЕН пристрій
  readonly telemetry = new EventLog<Reading>();
  readonly events    = new Topic<DomainEvent>();
  readonly jobs      = new WorkQueue<Job>();

  // пристрій вмикається — заводимо йому адресовану чергу з ним єдиним споживачем
  registerDevice(deviceId: string, onCommand: (c: Command) => void): void {
    const q = new Queue<Command>();
    q.subscribe(onCommand);                 // рівно ОДИН споживач — сам пристрій
    this.deviceQueues.set(deviceId, q);
  }

  command(deviceId: string, cmd: Command): void {
    const q = this.deviceQueues.get(deviceId);
    if (!q) throw new Error(`пристрій ${deviceId} не підключений`);
    q.send(cmd);                            // → у чергу САМЕ цього пристрою
  }
  append(r: Reading): void   { this.telemetry.append(r); }   // → журнал
  publish(e: DomainEvent): void { this.events.publish(e); }  // → тема
  enqueue(j: Job): void      { this.jobs.submit(j); }        // → робоча черга
}
