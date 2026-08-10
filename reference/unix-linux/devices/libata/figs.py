import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def main():
    w, h = 700, 450
    frags = []
    
    frags.append(textbox(350, 80, "Простір користувача (fdisk, mkfs, hdparm, smartctl)", min_w=500, rx=10, fill="#f4f6f8")[0])
    frags.append(arrow(350, 110, 350, 150))
    frags.append(textbox(350, 180, "SCSI Mid-layer\n(універсальний шар, пристрої /dev/sdX)", min_w=500, rx=10)[0])
    frags.append(arrow(350, 210, 350, 250))
    frags.append(textbox(350, 280, "libata\n(Трансляція SAT: SCSI-to-ATA Translation)", min_w=500, rx=10, fill="#eaf0fd", stroke=NEG)[0])
    frags.append(arrow(350, 310, 350, 350))
    frags.append(textbox(350, 380, "Апаратний контролер (AHCI / SATA / IDE)", min_w=500, rx=10, fill="#fdecea", stroke=POS)[0])
    
    outdir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(outdir, exist_ok=True)
    render(os.path.join(outdir, "libata-arch.svg"), w, h, *frags, title="Архітектура підсистеми libata в ядрі Linux")

if __name__ == "__main__":
    main()
