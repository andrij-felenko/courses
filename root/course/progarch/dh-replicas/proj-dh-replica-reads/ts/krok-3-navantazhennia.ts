function run(lagWindow = 1.5, classify = true, sticky = true, pin = true,
             nHomes = 400, steps = 5000, dt = 0.02, seed = 42) {
  const rng = new Rng(seed);
  const c = new Cluster([0.2, 0.5, 1.0]);     // три фоловери з різним лагом, с
  const r = new ReadRouter(c, lagWindow, classify, sticky, pin, new Rng(7));

  // елемент watch: [момент, home, device, seq запису, номер серії]
  let watch: [number, number, number, number, number][] = [];
  const burstSeen = new Map<number, number>();
  const served = { leader: 0, follower: 0 };
  let ryw = 0, viol = 0, mono = 0, rereadLeader = 0, burst = 0;

  const doRead = (home: number, device: number, kind: Kind): [Leader | Follower, Cell | undefined] => {
    const node = r.route(home, kind);
    if (node === c.leader) served.leader++; else served.follower++;
    return [node, node.get(home, device)];
  };

  for (let i = 0; i < steps; i++) {
    // ~3% кроків: користувач клацає пристрій і за мить перечитує екран 4 рази
    if (rng.below(0.03)) {
      const home = rng.index(nHomes), device = rng.index(4);
      const seq = c.write(home, device, rng.pick(["on", "off"]));
      r.noteWrite(home); burst++;
      for (const d of [0.15, 0.35, 0.6, 0.9]) watch.push([c.clock.t + d, home, device, seq, burst]);
    }
    const due = watch.filter(w => w[0] <= c.clock.t);
    if (due.length) {
      watch = watch.filter(w => w[0] > c.clock.t);
      for (const [, home, device, wseq, b] of due) {
        const [node, got] = doRead(home, device, "device_state");
        if (node === c.leader) rereadLeader++;
        ryw++;
        const gseq = got ? got[1] : -1;
        if (gseq < wseq) viol++;                             // не бачу власного запису
        if (gseq < (burstSeen.get(b) ?? -1)) mono++;         // час пішов назад
        burstSeen.set(b, Math.max(burstSeen.get(b) ?? -1, gseq));
      }
    }
    for (let k = 0; k < 6; k++) {               // фоновий потік
      const u = rng.next();
      const kind: Kind = u < 0.55 ? "telemetry" : u < 0.78 ? "registry"
        : u < 0.92 ? "device_state" : "lock";
      doRead(rng.index(nHomes), rng.index(4), kind);
    }
    c.tick(dt);
  }
  const total = served.leader + served.follower;
  return { ryw, viol, mono, rereadLeader, leaderFrac: served.leader / total,
           followerFrac: served.follower / total, total };
}

const base = run(1.5, false, true, false);    // наївний балансувальник
const good = run();                           // класи + липке + прив'язка
console.log(`БЕЗ  маршрутизації: ${base.viol}/${base.ryw} перечитувань застарілих ` +
  `(${Math.round(100*base.viol/base.ryw)}%), ${base.mono} стрибків часу назад; ` +
  `лідер ${Math.round(100*base.leaderFrac)}%`);
console.log(`З    маршрутизацією: ${good.viol} застарілих, ${good.mono} стрибків; ` +
  `лідер ${(100*good.leaderFrac).toFixed(1)}%, фоловери ${(100*good.followerFrac).toFixed(1)}% ` +
  `(усього ${good.total} читань)`);
