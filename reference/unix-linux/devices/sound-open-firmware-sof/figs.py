import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_arch():
    frags = []
    
    # 1. Userspace Layer
    h1, _, _ = textbox(120, 60, "Користувацький простір", size=12, bold=True, fill="#f2f4f8", stroke="#4a5568")
    b1, _, _ = textbox(360, 60, "PipeWire / PulseAudio / ALSA-lib", size=11, fill="#ffffff", stroke="#cbd5e0")
    b2, _, _ = textbox(620, 60, "alsatplg / Topology Tools", size=11, fill="#ffffff", stroke="#cbd5e0")
    frags.extend([h1, b1, b2])

    # Arrows Userspace -> Kernel
    frags.append(arrow(360, 80, 360, 115, color="#718096", sw=1.5))
    frags.append(arrow(620, 80, 620, 115, color="#718096", sw=1.5))

    # 2. Kernel Space Layer
    h2, _, _ = textbox(120, 140, "Ядро Linux (ASoC)", size=12, bold=True, fill="#ebf8ff", stroke="#3182ce")
    kb1, _, _ = textbox(300, 140, "ASoC DPCM (FE/BE)\n& ALSA Core", size=10, fill="#ffffff", stroke="#90cdf4")
    kb2, _, _ = textbox(470, 140, "snd_sof Core\nTopology & IPC Parser", size=10, fill="#ffffff", stroke="#90cdf4")
    kb3, _, _ = textbox(660, 140, "snd_sof_dsp_ops\n(Intel HDA / NXP)", size=10, fill="#ffffff", stroke="#90cdf4")
    frags.extend([h2, kb1, kb2, kb3])

    # Arrows Kernel -> Shared Mailbox
    frags.append(arrow(470, 165, 470, 205, color="#3182ce", sw=1.5))
    frags.append(arrow(660, 165, 660, 205, color="#3182ce", sw=1.5))
    
    # 3. Hardware Interconnect (Mailbox SRAM)
    mb, _, _ = textbox(470, 225, "PCIe / MMIO Mailbox SRAM & Doorbell Registers", size=11, fill="#feebc8", stroke="#dd6b20")
    frags.append(mb)

    # Arrow Mailbox -> DSP
    frags.append(arrow(470, 245, 470, 285, color="#dd6b20", sw=1.5))

    # 4. Audio DSP Space Layer
    h3, _, _ = textbox(120, 310, "Sound Open Firmware", size=12, bold=True, fill="#f0fff4", stroke="#38a169")
    db1, _, _ = textbox(290, 310, "Zephyr RTOS Core\n(Scheduler & Memory)", size=10, fill="#ffffff", stroke="#9ae6b4")
    db2, _, _ = textbox(470, 310, "IPC Server\nMessage Handler", size=10, fill="#ffffff", stroke="#9ae6b4")
    db3, _, _ = textbox(660, 310, "Audio Pipeline\n(Host DMA -> EQ -> DAI)", size=10, fill="#ffffff", stroke="#9ae6b4")
    frags.extend([h3, db1, db2, db3])

    # Output Arrow -> Codec
    frags.append(arrow(660, 335, 660, 375, color="#38a169", sw=1.5))
    
    # 5. External Hardware Codec
    cb, _, _ = textbox(660, 395, "Зовнішній аудіокодек (I2S / SoundWire)", size=10, fill="#edf2f7", stroke="#718096")
    frags.append(cb)

    filepath = os.path.join(IMG, "sof-arch.svg")
    render(filepath, 800, 430, *frags, title="Архітектура SOF та ALSA SoC")

def render_pcm_flow():
    frags = []
    
    # Step 1: Open / HW Params
    b1, _, _ = textbox(130, 60, "1. pcm_open / hw_params", size=9.5, fill="#ffffff", stroke="#a0aec0")
    frags.append(b1)
    frags.append(arrow(200, 60, 235, 60, color="#4a5568", sw=1.2))
    
    b2, _, _ = textbox(310, 60, "2. SOF_IPC_STREAM_PARAMS\nВиділення Ring Buffer", size=9.5, fill="#ffffff", stroke="#63b3ed")
    frags.append(b2)
    frags.append(arrow(385, 60, 415, 60, color="#3182ce", sw=1.2))
    
    b3, _, _ = textbox(490, 60, "3. Host DRAM Buffer\nMailbox IPC Cmd", size=9.5, fill="#ffffff", stroke="#f6ad55")
    frags.append(b3)
    frags.append(arrow(565, 60, 595, 60, color="#dd6b20", sw=1.2))

    b4, _, _ = textbox(670, 60, "4. Налаштування Pipeline\nHost DMA & DAI DMA", size=9.5, fill="#ffffff", stroke="#68d391")
    frags.append(b4)

    # Step 2: Trigger Start
    b5, _, _ = textbox(130, 140, "5. writei() PCM даних", size=9.5, fill="#ffffff", stroke="#a0aec0")
    frags.append(b5)
    frags.append(arrow(200, 140, 415, 140, color="#4a5568", sw=1.2))

    b6, _, _ = textbox(490, 140, "6. Запис PCM у Ring Buffer", size=9.5, fill="#ffffff", stroke="#f6ad55")
    frags.append(b6)

    b7, _, _ = textbox(310, 210, "7. TRIGGER_START (IPC)", size=9.5, fill="#ffffff", stroke="#63b3ed")
    frags.append(b7)
    frags.append(arrow(385, 210, 595, 210, color="#3182ce", sw=1.2))

    b8, _, _ = textbox(670, 210, "8. Старт Host DMA\nОбробка ефектами", size=9.5, fill="#ffffff", stroke="#68d391")
    frags.append(b8)

    # Step 3: Period elapsed callback
    b9, _, _ = textbox(670, 280, "9. Period Complete\nIPC Position Update", size=9.5, fill="#ffffff", stroke="#68d391")
    frags.append(b9)
    frags.append(arrow(595, 280, 385, 280, color="#38a169", sw=1.2))

    b10, _, _ = textbox(310, 280, "10. Interrupt IRQ\nsnd_pcm_period_elapsed()", size=9.5, fill="#ffffff", stroke="#63b3ed")
    frags.append(b10)
    frags.append(arrow(235, 280, 200, 280, color="#3182ce", sw=1.2))

    b11, _, _ = textbox(130, 280, "11. Пробудження poll()\nЗапис наступної порції", size=9.5, fill="#ffffff", stroke="#a0aec0")
    frags.append(b11)

    filepath = os.path.join(IMG, "sof-pcm-flow.svg")
    render(filepath, 800, 340, *frags, title="Життєвий цикл PCM потоку SOF")

if __name__ == '__main__':
    render_arch()
    render_pcm_flow()
