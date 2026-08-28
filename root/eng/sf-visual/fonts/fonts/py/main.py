# Кадровий буфер RGB565: WIDTH×HEIGHT, рядок за рядком
fb = [0] * (WIDTH * HEIGHT)

# Один гліф 8×8: 8 байтів, старший біт — лівий піксель рядка
def blit_glyph(x, y, glyph, color):
    for row in range(8):
        bits = glyph[row]                   # рядок гліфа
        for col in range(8):
            if bits & (0x80 >> col):        # біт виставлено → піксель чорний
                fb[(y + row) * WIDTH + (x + col)] = color

# Рядок тексту: блітнути гліф і зсунути курсор на крок (тут моноширинний — 8)
def draw_text(x, y, s, color):
    cursor = x
    for ch in s:
        g = font8x8[ord(ch)]                # код символу → 8 байтів гліфа
        blit_glyph(cursor, y, g, color)
        cursor += 8                         # advance: наступна літера праворуч
