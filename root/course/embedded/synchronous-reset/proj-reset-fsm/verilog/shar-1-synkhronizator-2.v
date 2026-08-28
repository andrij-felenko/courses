// Те саме, але rst активний ВИСОКИМ (1 = скидати). Гілка — posedge rst.
module reset_sync_ah (
    input  wire clk,
    input  wire rst,             // 1 = скидати, асинхронно
    output reg  rst_sync         // 1 = скидати, чисте зняття
);
    reg ff1;
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            ff1      <= 1'b1;    // assert умить
            rst_sync <= 1'b1;
        end else begin
            ff1      <= 1'b0;    // зняття вповзає за два такти
            rst_sync <= ff1;
        end
    end
endmodule
