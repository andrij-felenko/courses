// Двоє дверей — двоє тонких адаптерів на ОДИН сервіс. Логіки в них нема.

function runLoop(hub: HubService): void {           // двері 1: автономний цикл
  setInterval(() => hub.tick(), 30_000);            // єдиний виклик — сценарій tick
}

function runCli(hub: HubService, argv: string[]): void {   // двері 2: команда в терміналі
  const [cmd, ...rest] = argv;
  if (cmd === "state")              console.log(hub.state());
  else if (cmd === "set-threshold") hub.setThreshold(Number(rest[0]));
  else if (cmd === "add")           hub.addDevice({ kind: rest[0], room: rest[1] });
}
