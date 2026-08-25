import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
try:
    import svgkit
except ImportError:
    print("WARNING: svgkit not found")
    sys.exit(0)

W, H = 800, 440
os.makedirs("img", exist_ok=True)

out = []
# SCSI CDB
out.append(svgkit.rect(265, 80, 250, 56))
out.append(svgkit.text(390, 114, "SCSI CDB — напр. READ(10)", size=15, bold=True))

# Arrow down: CDB лягає всередину BHS
out.append(svgkit.arrow(390, 136, 390, 228))

# iSCSI PDU
out.append(svgkit.rect(230, 180, 480, 140, fill="#e0f0ff", stroke="#0044aa"))
out.append(svgkit.text(310, 206, "iSCSI PDU", size=16, bold=True))

out.append(svgkit.rect(250, 230, 270, 72, fill="#fff"))
out.append(svgkit.mtext(385, 258, ["BHS — заголовок, 48 байтів",
                                   "усередині: поле на 16 байтів під CDB"], size=12))

out.append(svgkit.rect(540, 230, 150, 72, fill="#fff"))
out.append(svgkit.mtext(615, 258, ["Data Segment —", "самі дані"], size=12))

# Arrow down
out.append(svgkit.arrow(470, 320, 470, 356))

# TCP/IP
out.append(svgkit.rect(230, 356, 480, 60, fill="#e0ffe0", stroke="#00aa00"))
out.append(svgkit.text(470, 392, "TCP/IP — кадри Ethernet, порт 3260", size=14, bold=True))

svgkit.render("img/encapsulation.svg", W, H, *out, title="Інкапсуляція SCSI в iSCSI")
print("Generated img/encapsulation.svg")
