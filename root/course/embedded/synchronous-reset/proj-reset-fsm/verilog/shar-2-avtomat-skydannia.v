module reset_fsm #(
    parameter SOFT_CYCLES = 16           // скільки тактів тримати в SOFT
) (
    input  wire clk,
    input  wire rst_sync_n,              // ВЖЕ синхронізоване зовнішнє скидання
    input  wire pll_locked,              // 1 = PLL зловив частоту
    output reg  core_rst_n,              // скидання ядра (1 = працювати)
    output reg  out_enable               // дозвіл на виходи в зовнішній світ
);
    localparam RESET    = 2'd0,
               WAIT_PLL = 2'd1,
               SOFT     = 2'd2,
               RUN      = 2'd3;

    reg [1:0] state;
    reg [4:0] cnt;                       // лічильник тактів для стану SOFT

    always @(posedge clk or negedge rst_sync_n) begin
        if (!rst_sync_n) begin
            // АСИНХРОННЕ падіння в корінь: будь-яка аварія — миттєво сюди
            state      <= RESET;
            cnt        <= 5'd0;
            core_rst_n <= 1'b0;          // ядро скинуте
            out_enable <= 1'b0;          // виходи перекриті — це найважливіше
        end else begin
            case (state)
                RESET: begin
                    core_rst_n <= 1'b0;
                    out_enable <= 1'b0;
                    state      <= WAIT_PLL;   // skидання знято — рушаємо чекати такт
                end
                WAIT_PLL: begin
                    if (pll_locked) begin
                        cnt   <= SOFT_CYCLES[4:0];
                        state <= SOFT;
                    end
                    // інакше лишаємося тут і тримаємо все скинутим
                end
                SOFT: begin
                    core_rst_n <= 1'b1;       // ядро вже можна будити...
                    if (cnt == 5'd0)
                        state <= RUN;
                    else
                        cnt <= cnt - 5'd1;     // ...але виходи ще тримаємо
                end
                RUN: begin
                    core_rst_n <= 1'b1;
                    out_enable <= 1'b1;        // аж ТЕПЕР пускаємо у світ
                end
                default: state <= RESET;       // ловець «неможливих» станів
            endcase
        end
    end
endmodule
