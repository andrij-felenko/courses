// Синхронізатор скидання: async assert, sync de-assert.
// rst_n активний НИЗЬКИМ (0 = «скидати»). Вихід rst_sync_n — теж активно-низький.
module reset_sync (
    input  wire clk,          // такт ЦЬОГО домену
    input  wire rst_n,        // асинхронне зовнішнє скидання (0 = скидати)
    output wire rst_sync_n    // у логіку домену: 0 = скидати, чисте зняття
);
    reg ff1, ff2;

    // АСИНХРОННА гілка в списку чутливості: posedge clk АБО negedge rst_n.
    // Саме negedge rst_n робить вмикання миттєвим, без чекання фронту такту.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ff1 <= 1'b0;      // assert: обидва тригери в 0 ВМИТЬ
            ff2 <= 1'b0;
        end else begin
            ff1 <= 1'b1;      // після зняття rst_n «1» вповзає за такт
            ff2 <= ff1;       // ...і ще за такт доходить виходу
        end
    end

    assign rst_sync_n = ff2;  // у логіку віддаємо ТІЛЬКИ другий тригер
endmodule
