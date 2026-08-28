// Модуль опитування геймпада та передачі команд керування
export class FlightControllerInput {
    private controlChannel: RTCDataChannel;
    private timerId: number | null = null;

    constructor(peerConnection: RTCPeerConnection) {
        // Створюємо ненадійний невпорядкований канал без повторів
        this.controlChannel = peerConnection.createDataChannel("controls", {
            ordered: false,
            maxRetransmits: 0
        });
        this.controlChannel.binaryType = "arraybuffer";

        this.controlChannel.onopen = () => {
            this.startControlLoop();
        };

        this.controlChannel.onclose = () => {
            this.stopControlLoop();
        };
    }

    private startControlLoop(): void {
        // Цикл опитування кожні 10 мс (100 Гц)
        this.timerId = window.setInterval(() => {
            this.pollAndSendStickCommands();
        }, 10);
    }

    private stopControlLoop(): void {
        if (this.timerId !== null) {
            clearInterval(this.timerId);
            this.timerId = null;
        }
    }

    private pollAndSendStickCommands(): void {
        if (this.controlChannel.readyState !== "open") return;

        const gamepads = navigator.getGamepads();
        const gp = gamepads[0];
        if (!gp) return;

        // Нормалізація стіків (-1.0 .. +1.0) у 16-бітові цілі числа (1000 .. 2000 мкс ШІМ)
        const throttlePwm = Math.round(1500 + (-gp.axes[1]) * 500); // Лівий стік Y (інвертований)
        const rollPwm     = Math.round(1500 + (gp.axes[2]) * 500);  // Правий стік X
        const pitchPwm    = Math.round(1500 + (-gp.axes[3]) * 500); // Правий стік Y
        const yawPwm      = Math.round(1500 + (gp.axes[0]) * 500);  // Лівий стік X

        const buffer = new ArrayBuffer(10);
        const view = new DataView(buffer);

        view.setUint16(0, throttlePwm, true);
        view.setUint16(2, rollPwm, true);
        view.setUint16(4, pitchPwm, true);
        view.setUint16(6, yawPwm, true);
        view.setUint8(8, gp.buttons[0].pressed ? 1 : 0); // Тумблер Arm
        view.setUint8(9, gp.buttons[1].pressed ? 1 : 0); // Тумблер Mode

        // Відправка без буферизації
        this.controlChannel.send(buffer);
    }
}
