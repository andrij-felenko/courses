`timescale 1ns/1ps          // одиниця часу — 1 нс

module tb;                  // тестбенч: жодного виводу назовні
    reg  clk = 0;           // сигнали, якими годуємо DUT
    reg  rst = 1;
    reg  en  = 0;
    wire [3:0] count;       // вихід DUT читаємо сюди

    counter dut (           // під'єднуємо DUT (наш дизайн)
        .clk(clk), .rst(rst), .en(en), .count(count));

    always #5 clk = ~clk;   // такт: період 10 нс, живе весь час

    initial begin           // сценарій: розгортається один раз
        #12  rst = 0;       // за 12 нс зняти скидання
        #10  en  = 1;       // ще за 10 нс дозволити лік
        #200 $finish;       // за 200 нс завершити симуляцію
    end
endmodule
