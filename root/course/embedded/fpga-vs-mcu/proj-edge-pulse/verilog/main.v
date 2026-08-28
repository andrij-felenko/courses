// Детектор наростального фронту на кожен канал.
// N копій логіки = N ділянок кремнію, що працюють одночасно.
module edge_pulse #(parameter N = 4) (
    input  wire         clk,
    input  wire [N-1:0] din,            // IN0..IN3 (вже синхронізовані, див. нижче)
    output reg  [N-1:0] pulse           // OUT0..OUT3: імпульс на 1 такт
);
    reg [N-1:0] prev;
    always @(posedge clk) begin
        pulse <= din & ~prev;           // усі N розрядів рахуються ПАРАЛЕЛЬНО
        prev  <= din;
    end
endmodule
