template <BusDevice BusImpl>
void runSensorWorker(Bmp280Driver<BusImpl>& driver, std::binary_semaphore& dmaReadySignal) {
    while (true) {
        driver.startReadDma();

        if (dmaReadySignal.try_acquire_for(std::chrono::milliseconds(100))) {
            if (auto sample = driver.readSynchronous(); sample.has_value()) {
                processBarometerFusion(*sample);
            }
        } else {
            driver.recoverBus();
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
}
