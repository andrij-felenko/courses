// 16 слів по 8 біт — сяде в кілька LUT як розподілене ОЗП.
// Ключ до впізнавання: читання БЕЗ такту, запис ПІД фронтом.
module regfile16x8 (
    input              clk,
    input              we,          // дозвіл запису (write enable)
    input      [3:0]   waddr,       // адреса запису (4 біти → 16 комірок)
    input      [7:0]   wdata,       // дані запису
    input      [3:0]   raddr,       // адреса читання
    output     [7:0]   rdata        // дані читання
);
    reg [7:0] mem [0:15];           // 16×8 — тіло пам'яті

    always @(posedge clk)           // ЗАПИС — синхронний, по фронту й за we
        if (we)
            mem[waddr] <= wdata;

    assign rdata = mem[raddr];      // ЧИТАННЯ — асинхронне, без такту
endmodule
