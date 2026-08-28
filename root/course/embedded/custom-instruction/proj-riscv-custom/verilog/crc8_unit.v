// crc8_unit.v — один крок CRC-8 над байтом, комбінаційно.
// Глибша схема, ніж popcount: 8 умовних XOR поспіль.
module crc8_unit (
    input  wire [7:0] data,        // байт даних (молодші біти rs1)
    input  wire [7:0] crc_in,      // поточний стан CRC (молодші біти rs2)
    output wire [7:0] crc_out
);
    localparam [7:0] POLY = 8'h07;     // CRC-8: x^8 + x^2 + x + 1
    integer i;
    reg [7:0] c;
    always @(*) begin
        c = crc_in ^ data;
        for (i = 0; i < 8; i = i + 1)
            c = c[7] ? ((c << 1) ^ POLY) : (c << 1);
        // 8 умовних XOR -> довший комбінаційний ланцюг, ніж дерево popcount
    end
    assign crc_out = c;
endmodule
