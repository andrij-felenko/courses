# Повний конвеєр для однієї шини, заведеної на приймач.
def process_bus(net, bus_text, sink_pins):          # "D[7..0]", піни по порядку
    bn = parse_bus(bus_text)                        # 1) розбір
    if bn is None:
        print(f"ПОМИЛКА: не розібрати запис шини '{bus_text}'")
        return
    if bn.is_vector and bus_width(bn) != len(sink_pins):        # 2) звірка ширин
        print(f"ПОМИЛКА розрядності: шина {bus_text} — {bus_width(bn)} ліній, "
              f"приймач — {len(sink_pins)} пінів")

    attach_bus(net, bn, sink_pins)                  # 3) розгорнути й завести
    warn_dangling(net, bn)                          # 4) перевірити висячі члени
