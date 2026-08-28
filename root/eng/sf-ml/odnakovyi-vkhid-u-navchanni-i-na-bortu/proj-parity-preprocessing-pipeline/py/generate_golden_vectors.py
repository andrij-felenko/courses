# generate_golden_vectors.py
import numpy as np
import math

def float_to_q031(val):
    return int(round(val * (2**31)))

def generate_synthetic_dataset(width, height):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            img[y, x, 0] = int((math.sin(x / 10.0) + 1.0) * 127.5) # R
            img[y, x, 1] = (x * 255) // width                       # G
            img[y, x, 2] = (y * 255) // height                      # B
    return img

def rgb888_to_rgb565(img):
    r5 = (img[..., 0] >> 3) & 0x1F
    g6 = (img[..., 1] >> 2) & 0x3F
    b5 = (img[..., 2] >> 3) & 0x1F
    return ((r5 << 11) | (g6 << 5) | b5).astype(np.uint16)

def export_golden_vectors():
    in_w, in_h = 320, 240
    out_w, out_h = 224, 224
    
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float64)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float64)
    s_in = 0.007843137
    z_in = 0

    img_rgb = generate_synthetic_dataset(in_w, in_h)
    img_565 = rgb888_to_rgb565(img_rgb)
    img_565.tofile("test_input_qvga_rgb565.bin")

    golden_out = np.zeros((out_h, out_w, 3), dtype=np.int8)
    step_x = in_w / out_w
    step_y = in_h / out_h

    for oy in range(out_h):
        v = (oy + 0.5) * step_y - 0.5
        v_clamped = max(0.0, min(float(in_h - 1), v))
        y0 = int(math.floor(v_clamped))
        y1 = min(in_h - 1, y0 + 1)
        fy = v_clamped - y0

        for ox in range(out_w):
            u = (ox + 0.5) * step_x - 0.5
            u_clamped = max(0.0, min(float(in_w - 1), u))
            x0 = int(math.floor(u_clamped))
            x1 = min(in_w - 1, x0 + 1)
            fx = u_clamped - x0

            p00 = img_rgb[y0, x0]
            p10 = img_rgb[y0, x1]
            p01 = img_rgb[y1, x0]
            p11 = img_rgb[y1, x1]

            w00 = (1.0 - fx) * (1.0 - fy)
            w10 = fx * (1.0 - fy)
            w01 = (1.0 - fx) * fy
            w11 = fx * fy

            for c in range(3):
                interp = p00[c]*w00 + p10[c]*w10 + p01[c]*w01 + p11[c]*w11
                norm = ((interp / 255.0) - mean[c]) / std[c]
                q = int(round(norm / s_in)) + z_in
                golden_out[oy, ox, c] = np.clip(q, -128, 127)

    golden_out.tofile("golden_output_224_int8.bin")
    print("Golden vectors successfully exported.")

if __name__ == "__main__":
    export_golden_vectors()
