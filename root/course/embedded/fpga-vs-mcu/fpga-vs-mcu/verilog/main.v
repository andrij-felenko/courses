// Детектор фронту на кожен канал; чотири копії працюють одночасно.
// Жоден канал не чекає на інший — це різні ділянки кремнію.
module edge_pulse #(parameter N = 4) (
    input  wire           clk,
    input  wire [N-1:0]   din,         // IN0..IN3
    output reg  [N-1:0]   pulse        // OUT0..OUT3, імпульс на 1 такт
);
    reg [N-1:0] prev;
    always @(posedge clk) begin
        pulse <= din & ~prev;          // усі N каналів обчислюються паралельно
        prev  <= din;
    end
endmodule
