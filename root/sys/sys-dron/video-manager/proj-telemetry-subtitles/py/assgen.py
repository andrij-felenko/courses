#!/usr/bin/env python3
# запуск: python3 assgen.py 1280 720 30 > flight.ass
import math
import sys
from dataclasses import dataclass
from typing import Callable, List, Tuple

Reading = Tuple[str, str]                    # («Висота», «12.4 м»)
Sampler = Callable[[float], List[Reading]]


@dataclass(frozen=True)
class Layout:
    width: int = 1280
    height: int = 720
    columns: int = 3     # скільки пар «назва: значення» по горизонталі
    spread: int = 100    # наскільки розсунути крайні колонки до країв
    gap: int = 10        # просвіт між назвою і значенням
    bottom: int = 30     # відступ низу блока від низу кадру

    @property
    def font_size(self) -> int:
        return max(8, self.width * 12 // 640)

    def column_x(self, i: int) -> int:
        stride = (self.width + self.spread) // (self.columns + 1)
        return -(self.spread // 2) + stride * (i + 1)


def timecode(seconds: float) -> str:
    """H:MM:SS.cc — години однією цифрою, сотих рівно дві."""
    cs = max(0, round(seconds * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6_000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


# Стандарт ASS не має екранування: «{» відкриває блок команд, «\» починає
# команду, перенос рядка обриває подію. Вміст наш власний — просто не
# пускаємо ці знаки у файл.
_UNSAFE = str.maketrans({"{": "(", "}": ")", "\\": "/", "\n": " ", "\r": " "})


def sanitize(s: str) -> str:
    return s.translate(_UNSAFE)


def header(L: Layout) -> str:
    return (
        "[Script Info]\n"
        "Title: Telemetry overlay\n"
        "ScriptType: v4.00+\n"
        "WrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n"
        f"PlayResX: {L.width}\n"
        f"PlayResY: {L.height}\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,Monospace,{L.font_size},"
        "&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
        "0,0,0,0,100,100,0,0,1,2,2,1,10,10,10,1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text\n"
    )


def dialogue(t0: float, t1: float, x: int, y: int,
             align: str, text: str) -> str:
    return (f"Dialogue: 0,{timecode(t0)},{timecode(t1)},Default,,0,0,0,,"
            f"{{{align}\\pos({x},{y})}}{text}\n")


def write_subtitles(out, L: Layout, sample: Sampler,
                    duration: float, rate: float = 1.0) -> None:
    out.write(header(L))
    step = 1.0 / rate
    y = L.height - L.bottom

    k = 0
    while k * step < duration:
        t0, t1 = k * step, (k + 1) * step    # від номера, а не накопиченням
        k += 1

        readings = sample(t0)                # знімок на ПОЧАТКУ інтервалу
        if not readings:
            continue

        per = -(-len(readings) // L.columns)  # стеля ділення
        for c in range(L.columns):
            chunk = readings[c * per:(c + 1) * per]
            if not chunk:
                continue
            names = "\\N".join(f"{sanitize(n)}:" for n, _ in chunk)
            values = "\\N".join(sanitize(v) for _, v in chunk)
            x = L.column_x(c)
            out.write(dialogue(t0, t1, x - L.gap, y, r"\an3", names))
            out.write(dialogue(t0, t1, x, y, r"\an1", values))


def demo_flight(t: float) -> List[Reading]:
    return [
        ("Висота",     f"{40 * (1 - math.exp(-t / 12)):.1f} м"),
        ("Швидкість",  f"{8 + 3 * math.sin(t / 5):.1f} м/с"),
        ("Курс",       f"{(t * 9) % 360:.0f}°"),
        ("Батарея",    f"{16.8 - 0.004 * t:.2f} В"),
        ("Політ",      f"{t:.0f} с"),
        ("Супутники",  "12"),
        ("Режим",      "AUTO"),
    ]


if __name__ == "__main__":
    a = sys.argv[1:]
    L = Layout(width=int(a[0]), height=int(a[1])) if len(a) >= 2 else Layout()
    duration = float(a[2]) if len(a) >= 3 else 30.0
    rate = float(a[3]) if len(a) >= 4 else 1.0

    # UTF-8 і рівно «\n» — інакше на Windows у файл поїде «\r\n»
    out = open(sys.stdout.fileno(), "w", encoding="utf-8", newline="\n")
    write_subtitles(out, L, demo_flight, duration, rate)
    out.flush()
