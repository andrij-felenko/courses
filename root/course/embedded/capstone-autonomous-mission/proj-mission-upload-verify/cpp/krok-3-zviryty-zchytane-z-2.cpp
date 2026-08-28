int main(void) {
    open_udp("0.0.0.0", 14550);          // слухати SITL / телеметрію
    wait_heartbeat();                    // дізнатися TSYS/TCMP
    build_mission();

    if (!upload_mission(mission, N)) {
        fputs("завантаження провалилося — не армимося\n", stderr); return 1;
    }

    mavlink_mission_item_int_t readback[64]; uint16_t got = 0;
    if (!download_mission(readback, 64, &got)) {
        fputs("не зчиталося — не армимося\n", stderr); return 1;
    }
    if (!verify_mission(readback, got, mission, N, 0.5)) {
        fputs("звірка не збіглася — НЕ армимося, шукаємо різницю\n", stderr); return 1;
    }

    puts("\nмісія на борті збігається із задумом — можна армитися.");
    return 0;
}
