// TypeScript клієнт станції керування в браузері (GCS)

interface FlightTelemetry {
    timestampMs: number;
    rollDeg: number;
    pitchDeg: number;
    yawDeg: number;
    altitudeM: number;
    batteryVoltage: number;
    armState: number;
    flightMode: number;
}

export class TelemetryReceiver {
    private channel: RTCDataChannel | null = null;
    private onTelemetryCallback: ((data: FlightTelemetry) => void) | null = null;

    constructor(peerConnection: RTCPeerConnection) {
        // Прослуховуємо подію створення каналу віддаленим C++ агентом
        peerConnection.ondatachannel = (event: RTCDataChannelEvent) => {
            if (event.channel.label === "telemetry") {
                this.setupChannel(event.channel);
            }
        };
    }

    private setupChannel(channel: RTCDataChannel): void {
        this.channel = channel;
        this.channel.binaryType = "arraybuffer";

        this.channel.onopen = () => {
            console.log("Канал телеметрії WebRTC DataChannel успішно відкрито");
        };

        this.channel.onmessage = (event: MessageEvent) => {
            if (!(event.data instanceof ArrayBuffer)) return;

            const buffer = event.data;
            if (buffer.byteLength !== 32) {
                console.warn(`Некоректний розмір кадру: очікувалося 32 байти, отримано ${buffer.byteLength}`);
                return;
            }

            const view = new DataView(buffer);

            // Перевірка контрольної суми CRC-16
            const receivedCrc = view.getUint16(30, true);
            const computedCrc = this.computeCrc16(new Uint8Array(buffer, 0, 30));

            if (receivedCrc !== computedCrc) {
                console.error("Помилка перевірки CRC-16: пакет пошкоджено при передачі");
                return;
            }

            const telemetry: FlightTelemetry = {
                timestampMs: view.getUint32(0, true),
                rollDeg: view.getFloat32(4, true),
                pitchDeg: view.getFloat32(8, true),
                yawDeg: view.getFloat32(12, true),
                altitudeM: view.getFloat32(16, true),
                batteryVoltage: view.getFloat32(20, true),
                armState: view.getUint8(24),
                flightMode: view.getUint8(25)
            };

            if (this.onTelemetryCallback) {
                this.onTelemetryCallback(telemetry);
            }
        };
    }

    private computeCrc16(bytes: Uint8Array): number {
        let crc = 0xFFFF;
        for (let i = 0; i < bytes.length; ++i) {
            crc ^= bytes[i];
            for (let j = 0; j < 8; ++j) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0x8408;
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }

    public onTelemetry(callback: (data: FlightTelemetry) => void): void {
        this.onTelemetryCallback = callback;
    }
}
