import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit, якщо потрібно
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
try:
    import svgkit
except ImportError:
    # Заглушка, якщо svgkit недоступний
    class svgkit:
        @staticmethod
        def render(filename, width, height, content):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n{content}\n</svg>')

def render():
    deb_struct = """
    <rect x="10" y="10" width="380" height="280" fill="#f8f9fa" stroke="#6c757d" stroke-width="2" rx="5"/>
    <text x="20" y="40" font-family="sans-serif" font-size="20" font-weight="bold" fill="#343a40">.deb Package (ar archive)</text>
    
    <rect x="30" y="60" width="340" height="50" fill="#e9ecef" stroke="#adb5bd" stroke-width="1"/>
    <text x="40" y="90" font-family="sans-serif" font-size="16" fill="#495057">debian-binary (version info)</text>
    
    <rect x="30" y="130" width="340" height="60" fill="#e9ecef" stroke="#adb5bd" stroke-width="1"/>
    <text x="40" y="155" font-family="sans-serif" font-size="16" fill="#495057">control.tar.xz (metadata, scripts)</text>
    <text x="40" y="175" font-family="sans-serif" font-size="12" fill="#6c757d">control, preinst, postinst, prerm, postrm</text>
    
    <rect x="30" y="210" width="340" height="60" fill="#e9ecef" stroke="#adb5bd" stroke-width="1"/>
    <text x="40" y="235" font-family="sans-serif" font-size="16" fill="#495057">data.tar.xz (payload files)</text>
    <text x="40" y="255" font-family="sans-serif" font-size="12" fill="#6c757d">/usr/bin/..., /etc/..., /var/...</text>
    """
    
    rpm_struct = """
    <rect x="420" y="10" width="380" height="280" fill="#f8f9fa" stroke="#6c757d" stroke-width="2" rx="5"/>
    <text x="430" y="40" font-family="sans-serif" font-size="20" font-weight="bold" fill="#343a40">.rpm Package</text>
    
    <rect x="440" y="60" width="340" height="40" fill="#e9ecef" stroke="#adb5bd" stroke-width="1"/>
    <text x="450" y="85" font-family="sans-serif" font-size="16" fill="#495057">RPM Lead &amp; Signature</text>
    
    <rect x="440" y="110" width="340" height="60" fill="#e9ecef" stroke="#adb5bd" stroke-width="1"/>
    <text x="450" y="135" font-family="sans-serif" font-size="16" fill="#495057">Header</text>
    <text x="450" y="155" font-family="sans-serif" font-size="12" fill="#6c757d">Metadata (Name, Version, Requires...)</text>
    
    <rect x="440" y="180" width="340" height="90" fill="#e9ecef" stroke="#adb5bd" stroke-width="1"/>
    <text x="450" y="210" font-family="sans-serif" font-size="16" fill="#495057">Payload (cpio archive)</text>
    <text x="450" y="235" font-family="sans-serif" font-size="12" fill="#6c757d">Compressed files (xz/zstd)</text>
    <text x="450" y="255" font-family="sans-serif" font-size="12" fill="#6c757d">/usr/bin/..., /etc/..., /var/...</text>
    """
    
    svgkit.render(os.path.join(IMG, 'deb-vs-rpm.svg'), 820, 310, deb_struct + rpm_struct)

if __name__ == '__main__':
    render()
