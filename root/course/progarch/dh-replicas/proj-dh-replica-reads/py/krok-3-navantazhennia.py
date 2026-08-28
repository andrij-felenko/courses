def run(lag_window=1.5, classify=True, sticky=True, pin=True,
        n_homes=400, steps=5000, dt=0.02, seed=42):
    rng = Rng(seed)
    c = Cluster([0.2, 0.5, 1.0])              # три фоловери з різним лагом, с
    r = ReadRouter(c, lag_window, classify, sticky, pin, rng=Rng(7))

    watch, burst_seen = [], {}                # заплановані перечитування; макс. seq у серії
    served = {"leader": 0, "follower": 0}
    ryw = viol = mono = reread_leader = burst = 0

    def do_read(home, device, kind):
        node = r.route(home, kind)
        served["leader" if node is c.leader else "follower"] += 1
        return node, node.get(home, device)

    for _ in range(steps):
        # ~3% кроків: користувач клацає пристрій і за мить перечитує екран 4 рази
        if rng.below(0.03):
            home, device = rng.index(n_homes), rng.index(4)
            seq = c.write(home, device, rng.pick(["on", "off"]))
            r.note_write(home); burst += 1
            for d in (0.15, 0.35, 0.6, 0.9):
                watch.append((c.clock.t + d, home, device, seq, burst))

        due = [w for w in watch if w[0] <= c.clock.t]
        if due:
            watch = [w for w in watch if w[0] > c.clock.t]
            for _, home, device, wseq, b in due:
                node, got = do_read(home, device, "device_state")
                if node is c.leader: reread_leader += 1
                ryw += 1
                gseq = got[1] if got else -1
                if gseq < wseq: viol += 1                      # не бачу власного запису
                if gseq < burst_seen.get(b, -1): mono += 1     # час пішов назад
                burst_seen[b] = max(burst_seen.get(b, -1), gseq)

        for _ in range(6):                    # фоновий потік: телеметрія/реєстр/замок/чужий стан
            u = rng.next()
            kind = ("telemetry" if u < 0.55 else "registry" if u < 0.78
                    else "device_state" if u < 0.92 else "lock")
            do_read(rng.index(n_homes), rng.index(4), kind)

        c.tick(dt)

    total = served["leader"] + served["follower"]
    return dict(ryw=ryw, viol=viol, mono=mono, reread_leader=reread_leader,
                leader_frac=served["leader"] / total,
                follower_frac=served["follower"] / total, total=total)

if __name__ == "__main__":
    base = run(classify=False, pin=False)     # наївний балансувальник
    good = run()                              # класи + липке + прив'язка
    print("БЕЗ  маршрутизації: %d/%d перечитувань застарілих (%.0f%%), %d стрибків часу назад; "
          "лідер %.0f%%" % (base["viol"], base["ryw"], 100*base["viol"]/base["ryw"],
                            base["mono"], 100*base["leader_frac"]))
    print("З    маршрутизацією: %d застарілих, %d стрибків; лідер %.1f%%, фоловери %.1f%% "
          "(усього %d читань)" % (good["viol"], good["mono"], 100*good["leader_frac"],
                                  100*good["follower_frac"], good["total"]))
