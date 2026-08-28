`timescale 1ns/1ps
module uart_tx_tb;
    reg        clk   = 0;
    reg        start = 0;
    reg  [7:0] data  = 8'h41;  // байт 'A' (0x41) — щоб було що впізнати на хвилі
    wire       tx, busy;

    // DUT з навмисне малим дільником, щоб симуляція бігла швидко
    uart_tx #(.DIV(4)) dut (
        .clk(clk), .start(start), .data(data),
        .tx(tx), .busy(busy)
    );

    always #5 clk = ~clk;      // такт: період 10 нс

    initial begin
        $dumpfile("uart_tx.vcd");  // куди писати хвилі для перегляду
        $dumpvars(0, uart_tx_tb);
        @(negedge clk);
        start = 1; @(negedge clk); start = 0;  // імпульс "відправ" на один такт
        @(negedge busy);           // ждемо, доки кадр добіжить до кінця
        #50 $finish;
    end
endmodule
