DemoLink  link(14550);
LoopProbe probe;

QTimer report;
QObject::connect(&report, &QTimer::timeout, [&] {
    LinkStats &s = link.stats();
    qInfo("у черзі %lld · час у черзі %.1f мс · найдовший прогін %.1f мс · датаграм %lld",
          s.inFlight(),
          s.residenceMaxNs.load(std::memory_order_relaxed) / 1e6,
          probe.longestBusyNs() / 1e6,
          s.datagrams.load(std::memory_order_relaxed));
    s.residenceMaxNs.store(0, std::memory_order_relaxed);
    probe.reset();
});
report.start(1000);
