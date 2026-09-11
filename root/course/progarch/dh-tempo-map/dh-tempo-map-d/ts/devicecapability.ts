// Канонічні можливості фізичного обладнання
export type DeviceCapability = "binary-switch" | "dimmable" | "power-meter";

export interface DeviceProperties {
  power?: boolean;
  brightnessPercent?: number; // Фізична яскравість: 0..100%
  powerWatts?: number;        // Споживана потужність за системою SI
}

// Непорушний знімок стану пристрою
export interface CanonicalStateSnapshot {
  readonly deviceId: string;
  readonly capabilities: ReadonlySet<DeviceCapability>;
  readonly target: DeviceProperties;
  readonly actual: DeviceProperties;
  readonly lastConfirmedAt: number;
  readonly hasDiscrepancy: boolean;
}

// Канонічний агрегат ядра: містить лише фізичні реалії
export class CanonicalDevice {
  private targetState: DeviceProperties;
  private actualState: DeviceProperties;
  private lastConfirmationTime: number = 0;

  constructor(
    public readonly id: string,
    public readonly capabilities: Set<DeviceCapability>,
    initialActual: DeviceProperties
  ) {
    this.actualState = { ...initialActual };
    this.targetState = { ...initialActual };
  }

  // Прийом ідемпотентної команди мутації
  public applyCommand(mutation: Partial<DeviceProperties>): void {
    this.validateMutation(mutation);
    this.targetState = { ...this.targetState, ...mutation };
  }

  // Підтвердження фізичного стану від апаратного драйвера
  public confirmActual(confirmed: Partial<DeviceProperties>, timestamp: number): void {
    this.validateMutation(confirmed);
    this.actualState = { ...this.actualState, ...confirmed };
    this.lastConfirmationTime = timestamp;
  }

  public getSnapshot(): CanonicalStateSnapshot {
    const hasDiscrepancy =
      (this.targetState.power !== undefined && this.targetState.power !== this.actualState.power) ||
      (this.targetState.brightnessPercent !== undefined &&
        this.targetState.brightnessPercent !== this.actualState.brightnessPercent);

    return {
      deviceId: this.id,
      capabilities: new Set(this.capabilities),
      target: { ...this.targetState },
      actual: { ...this.actualState },
      lastConfirmedAt: this.lastConfirmationTime,
      hasDiscrepancy
    };
  }

  private validateMutation(props: Partial<DeviceProperties>): void {
    if (props.power !== undefined && !this.capabilities.has("binary-switch")) {
      throw new Error(`Пристрій ${this.id} не підтримує бінарне перемикання`);
    }
    if (props.brightnessPercent !== undefined && !this.capabilities.has("dimmable")) {
      throw new Error(`Пристрій ${this.id} не підтримує регулювання рівня`);
    }
  }
}

// Адаптер швидкої периферії: мобільний додаток підлаштовується під ядро
export class MobileUiDeviceAdapter {
  constructor(private readonly device: CanonicalDevice) {}

  public onUserToggle(requestedPower: boolean): void {
    // Формування канонічної команди мутації
    this.device.applyCommand({ power: requestedPower });
  }

  public buildViewModel(localizedName: string, activeThemeColor: string): object {
    const snapshot = this.device.getSnapshot();
    return {
      title: localizedName,
      color: activeThemeColor,
      isSwitching: snapshot.hasDiscrepancy,
      isOn: snapshot.actual.power ?? false,
      currentLoadWatts: snapshot.actual.powerWatts ?? 0
    };
  }
}
