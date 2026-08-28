// Затримати шину data на DEPTH тактів. Синтезатор згорне цей
// зсувний ланцюг у SRL — без витрати окремих тригерів на кожен щабель.
module delay_line #(parameter DEPTH = 16) (
    input              clk,
    input      [7:0]   din,
    output     [7:0]   dout
);
    reg [7:0] sr [0:DEPTH-1];       // ланцюг щаблів
    integer i;

    always @(posedge clk) begin
        sr[0] <= din;               // новий відлік заходить із входу
        for (i = 1; i < DEPTH; i = i + 1)
            sr[i] <= sr[i-1];       // уся низка крокує на щабель
    end

    assign dout = sr[DEPTH-1];      // вихід — з останнього щабля
endmodule
