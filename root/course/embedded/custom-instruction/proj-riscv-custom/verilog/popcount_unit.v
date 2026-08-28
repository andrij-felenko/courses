// popcount_unit.v — рахує одиничні біти 32-розрядного слова.
// Чиста комбінаційна логіка: результат готовий у тому ж такті.
module popcount_unit (
    input  wire [31:0] a,        // вхідне слово (це буде rs1)
    output wire [5:0]  count     // 0..32 одиниць -> вистачить 6 біт
);
    integer i;
    reg [5:0] sum;
    always @(*) begin
        sum = 6'd0;
        for (i = 0; i < 32; i = i + 1)
            sum = sum + a[i];     // синтезатор розгорне в дерево суматорів
        // НЕ цикл у часі: це 32 додавання, що існують одночасно в залізі
    end
    assign count = sum;
endmodule
