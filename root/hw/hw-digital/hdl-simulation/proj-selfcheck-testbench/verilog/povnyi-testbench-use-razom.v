`timescale 1ns/1ps

module tb_counter;
    reg        clk = 1'b0;
    reg        rst = 1'b1;      // стартуємо у скиді — виганяє X
    reg        en  = 1'b0;
    wire [3:0] count;           // жене ЛИШЕ DUT → wire
    reg  [3:0] expected = 4'd0; // еталон
    integer    checks   = 0;

    // під'єднуємо DUT (наш дизайн)
    counter dut (
        .clk(clk), .rst(rst), .en(en), .count(count));

    // вічний такт: період 10 нс, перший ↑фронт на t=5
    always #5 clk = ~clk;

    // ЕТАЛОН: те саме правило, той самий <=, той самий фронт
    always @(posedge clk) begin
        if (rst)            expected <= 4'd0;
        else if (en)        expected <= expected + 4'd1;
    end

    // ЗВІРКА: після защіпки (#0) count має дорівнювати expected
    always @(posedge clk) begin
        #0;
        if (count !== expected) begin
            $display("FAIL @ %0t: count=%b (%0d), чекали %b (%0d)",
                     $time, count, count, expected, expected);
            $finish;
        end
        checks = checks + 1;
    end

    // СЦЕНАРІЙ: входи міняємо на СПАДІ, у протифазі до защіпки
    initial begin
        @(negedge clk); @(negedge clk);  // тримаємо скид 2 фронти
        rst = 1'b0;                       // знімаємо скид
        @(negedge clk); @(negedge clk);  // 2 такти без дозволу — має стояти
        en  = 1'b1;                       // вмикаємо лічбу
        repeat (20) @(negedge clk);       // лічимо, з запасом на згортання
        rst = 1'b1; @(negedge clk); rst = 1'b0;  // скид посеред лічби
        repeat (5)  @(negedge clk);
        $display("PASS: усі %0d такти збіглися з еталоном", checks);
        $finish;                          // без цього — вічний такт
    end
endmodule
