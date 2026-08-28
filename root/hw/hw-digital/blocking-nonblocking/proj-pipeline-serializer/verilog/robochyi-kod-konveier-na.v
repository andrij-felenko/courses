module mac3 #(
    parameter W = 16                 // розрядність відліків
)(
    input                    clk,
    input      signed [W-1:0] a, b, c,        // три вхідні відліки
    input      signed [W-1:0] k1, k2, k3,     // три коефіцієнти
    output reg signed [2*W:0] y               // результат (з запасом на суму)
);
    // щабель 1: три добутки, защіпнуті в регістри
    reg signed [2*W-1:0] p1, p2, p3;
    // щабель 2: перша часткова сума
    reg signed [2*W:0]   s;

    always @(posedge clk) begin
        // щабель 1 — множення
        p1 <= a * k1;
        p2 <= b * k2;
        p3 <= c * k3;
        // щабель 2 — бере p1, p2 З МИНУЛОГО такту
        s  <= p1 + p2;
        // щабель 3 — бере s і p3 З МИНУЛОГО такту
        y  <= s + p3;
    end
endmodule
