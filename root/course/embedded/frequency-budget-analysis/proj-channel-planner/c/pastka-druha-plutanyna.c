// Іменовані множники — одиниця видно прямо в коді, помилитися важко.
#define MHZ  1.0e6
#define KHZ  1.0e3
#define GHZ  1.0e9

radio_spec ble = {
    .carrier_hz   = 2.4 * GHZ,     // читається як «2.4 гігагерца»
    .signal_bw_hz = 1.0 * MHZ,     // «1 мегагерц»
    .guard_hz     = 800.0 * KHZ,   // «800 кілогерц»
    // ...
};
