/* RAII блокування шини у C++20 */
{
    auto lock = bus.acquire_lock();
    cs_pin.set_level(hal::PinLevel::Low);

    bus.write(cmd_buf, 100);
    bus.read(data_buf, 100);

    cs_pin.set_level(hal::PinLevel::High);
} // М'ютекс шини автоматично звільняється при виході lock зі скоупу
