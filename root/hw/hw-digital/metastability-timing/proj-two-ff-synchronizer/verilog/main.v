// Синхронізатор живе в тактовому домені приймача (CLK).
// Атрибут ASYNC_REG підказує синтезатору тримати обидва тригери
// поряд, щоб метастабільність мала повний період на згасання.
module synchronizer (
    input  wire clk,        // такт приймача
    input  wire async_in,   // асинхронний вхід (кнопка, чужий домен)
    output wire clean_out   // визначений рівень для логіки
);
    (* ASYNC_REG = "TRUE" *) reg ff1, ff2;

    always @(posedge clk) begin
        ff1 <= async_in;    // 1-й щабель: може стати метастабільним
        ff2 <= ff1;         // 2-й щабель: за період ff1 уже згас
    end

    assign clean_out = ff2; // ТІЛЬКИ це віддаємо логіці
endmodule
