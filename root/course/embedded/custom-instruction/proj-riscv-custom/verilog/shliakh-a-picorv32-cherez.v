// Фрагмент верхнього рівня: ядро + наш PCPI-блок поруч.
wire        pcpi_valid, pcpi_wr, pcpi_wait, pcpi_ready;
wire [31:0] pcpi_insn, pcpi_rs1, pcpi_rs2, pcpi_rd;

picorv32 #(
    .ENABLE_PCPI(1)            // вмикаємо вивід PCPI назовні
) cpu (
    .clk(clk), .resetn(resetn),
    /* ... шина пам'яті тут ... */
    .pcpi_valid(pcpi_valid), .pcpi_insn(pcpi_insn),
    .pcpi_rs1(pcpi_rs1),     .pcpi_rs2(pcpi_rs2),
    .pcpi_wr(pcpi_wr),       .pcpi_rd(pcpi_rd),
    .pcpi_wait(pcpi_wait),   .pcpi_ready(pcpi_ready)
);

pcpi_popcount u_ci (
    .clk(clk), .resetn(resetn),
    .pcpi_valid(pcpi_valid), .pcpi_insn(pcpi_insn),
    .pcpi_rs1(pcpi_rs1),     .pcpi_rs2(pcpi_rs2),
    .pcpi_wr(pcpi_wr),       .pcpi_rd(pcpi_rd),
    .pcpi_wait(pcpi_wait),   .pcpi_ready(pcpi_ready)
);
