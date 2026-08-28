// counter.v — ДИЗАЙН (DUT), синтезовне залізо
module counter (
    input            clk,
    input            rst,     // синхронне скидання
    input            en,      // дозвіл лічби
    output reg [3:0] count
);
    always @(posedge clk) begin
        if (rst)
            count <= 4'd0;        // скид має пріоритет
        else if (en)
            count <= count + 4'd1; // лічимо тільки з дозволом
        // якщо ні rst, ні en — count тримає значення
    end
endmodule
