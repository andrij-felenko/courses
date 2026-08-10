import os
import sys

# Додаємо scripts до PYTHONPATH, щоб імпортувати svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))

try:
    from svgkit import svgkit
except ImportError:
    # Dummy svgkit for fallback if script is missing
    class SvgKitFallback:
        def __init__(self, filename, width, height):
            self.filename = filename
            self.content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        
        def text(self, x, y, text, **kwargs):
            self.content += f'<text x="{x}" y="{y}">{text}</text>'
        
        def rect(self, x, y, width, height, **kwargs):
            self.content += f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="none" stroke="black"/>'
        
        def render(self):
            self.content += '</svg>'
            with open(self.filename, 'w') as f:
                f.write(self.content)
    
    svgkit = SvgKitFallback

def draw_dma_buf_heaps_arch():
    ctx = svgkit('E:/develop/courses/reference/unix-linux/io/dma-buf-heaps-framework/dma_buf_heaps_arch.svg', 800, 500)
    
    # User space
    ctx.rect(50, 50, 700, 150, fill='#e0f7fa', stroke='#006064', rx=10)
    ctx.text(400, 80, 'User Space', font_size=20, font_weight='bold', text_anchor='middle', fill='#006064')
    
    ctx.rect(100, 110, 150, 60, fill='#fff', stroke='#00838f', rx=5)
    ctx.text(175, 145, 'V4L2 App (Camera)', text_anchor='middle', font_size=14)

    ctx.rect(325, 110, 150, 60, fill='#fff', stroke='#00838f', rx=5)
    ctx.text(400, 145, 'Allocator (DMA Heap)', text_anchor='middle', font_size=14)
    
    ctx.rect(550, 110, 150, 60, fill='#fff', stroke='#00838f', rx=5)
    ctx.text(625, 145, 'DRM App (Display)', text_anchor='middle', font_size=14)
    
    # Kernel space
    ctx.rect(50, 250, 700, 200, fill='#fff8e1', stroke='#ff8f00', rx=10)
    ctx.text(400, 280, 'Kernel Space', font_size=20, font_weight='bold', text_anchor='middle', fill='#ff8f00')
    
    ctx.rect(325, 300, 150, 60, fill='#fff', stroke='#e65100', rx=5)
    ctx.text(400, 335, 'DMA-BUF Heaps', text_anchor='middle', font_size=14)
    
    ctx.rect(100, 380, 150, 60, fill='#fff', stroke='#e65100', rx=5)
    ctx.text(175, 415, 'V4L2 Driver', text_anchor='middle', font_size=14)
    
    ctx.rect(550, 380, 150, 60, fill='#fff', stroke='#e65100', rx=5)
    ctx.text(625, 415, 'DRM Driver', text_anchor='middle', font_size=14)
    
    # Memory
    ctx.rect(325, 400, 150, 40, fill='#e8f5e9', stroke='#2e7d32', rx=5)
    ctx.text(400, 425, 'Physical Memory', text_anchor='middle', font_size=14)
    
    ctx.render()

def main():
    draw_dma_buf_heaps_arch()

if __name__ == '__main__':
    main()
