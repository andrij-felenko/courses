import numpy as np

def xy_trace(fx, fy, phase=0.0, ax=1.0, ay=1.0, fs=48_000.0, loops=1):
    """Слід точки за loops спільних періодів. Остання точка НЕ дублює першу."""
    T, p, q = common_period(fx, fy)
    n = int(round(fs * T * loops))
    t = np.arange(n) / fs
    return (ax * np.sin(2 * np.pi * fx * t + phase),
            ay * np.sin(2 * np.pi * fy * t))


def write_svg(path, x, y, size=420, pad=20):
    """XY-слід у файл SVG: масштаб по розмаху кожної осі, ламана замкнена."""
    r = (size - 2 * pad) / 2
    sx, sy = r / np.max(np.abs(x)), r / np.max(np.abs(y))
    c = size / 2
    pts = " ".join("%.2f,%.2f" % (c + sx * xi, c - sy * yi) for xi, yi in zip(x, y))
    with open(path, "w", encoding="utf-8") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">'
                '<rect width="%d" height="%d" fill="#fff"/>'
                '<polygon points="%s" fill="none" stroke="#2457d6" stroke-width="1.6"/>'
                '</svg>' % (size, size, size, size, pts))
