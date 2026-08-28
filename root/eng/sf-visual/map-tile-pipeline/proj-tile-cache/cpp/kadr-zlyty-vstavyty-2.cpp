void workerLoop(TileScheduler& sched, ReadyQueue& ready, TileSource& source) {
    Request r;
    TileScheduler::FlightPtr flight;
    while (sched.take(r, flight)) {
        TileScheduler::FlightGuard guard(sched, r.id);   // запис зникне за БУДЬ-ЯКОГО виходу

        std::vector<uint8_t> encoded;
        if (!source.fetch(r.id, encoded, *flight)) continue;   // 404, обрив, скасування

        Raster raster;
        if (!decode(encoded, raster)) continue;

        // Байти вже заплачено. Навіть якщо тайл застарів для екрана — він піде
        // в кеш; рішення «малювати чи ні» ухвалює потік малювання, не ми.
        ready.publish(Ready{ r.id,
                             std::make_shared<const Raster>(std::move(raster)),
                             r.generation });
    }
}
