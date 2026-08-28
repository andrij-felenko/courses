// Повний конвеєр для однієї шини, заведеної на приймач.
static void process_bus(Netlist& net,
                        const std::string& bus_text,        // "D[7..0]"
                        const std::vector<Pin>& sink_pins)  // піни приймача по порядку
{
    BusName bn;
    if (!parse_bus(bus_text, bn)) {                 // 1) розбір
        printf("ПОМИЛКА: не розібрати запис шини '%s'\n", bus_text.c_str());
        return;
    }
    if (bn.is_vector && bus_width(bn) != (int)sink_pins.size())  // 2) звірка ширин
        printf("ПОМИЛКА розрядності: шина %s — %d ліній, приймач — %zu пінів\n",
               bus_text.c_str(), bus_width(bn), sink_pins.size());

    attach_bus(net, bn, sink_pins);                 // 3) розгорнути й завести
    warn_dangling(net, bn);                         // 4) перевірити висячі члени
}
