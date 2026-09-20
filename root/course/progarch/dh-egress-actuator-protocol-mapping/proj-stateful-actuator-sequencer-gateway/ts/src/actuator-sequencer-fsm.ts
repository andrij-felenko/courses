/**
 * Скінченний автомат секвенсера дій актуатора (ActuatorSequencerFsm).
 * Забезпечує детерміновану координацію кроків життєвого циклу:
 * 1. CHECKING_POWER — перевірка наявності та стабільності силового живлення.
 * 2. RELEASING_BRAKE — розтискання стопорного гальма перед початком обертання.
 * 3. APPLYING_TORQUE — подача тяги на обмотки двигуна у потрібному напрямку.
 * 4. MOVING — фаза переміщення з контролем положення та квантовим опитуванням.
 * 5. VERIFYING_POSITION — точна верифікація координати після зупинки.
 * 6. ENGAGING_BRAKE — затискання механічного гальма для фіксації положення.
 * 7. HOLDING — стабільне утримання цільової точки.
 */
import { ActuatorHardwareSimulator } from './hardware-simulator.ts';
import { ActuatorState, Percentage } from './types.ts';

export class ActuatorSequencerFsm {
  private currentState: ActuatorState = ActuatorState.IDLE;
  private readonly stateHistory: ActuatorState[] = [];

  constructor() {
    this.transitionTo(ActuatorState.IDLE);
  }

  public getState(): ActuatorState {
    return this.currentState;
  }

  public getHistory(): readonly ActuatorState[] {
    return this.stateHistory;
  }

  public transitionTo(nextState: ActuatorState): void {
    this.currentState = nextState;
    this.stateHistory.push(nextState);
  }

  /**
   * Фаза 1: Перевірка живлення.
   */
  public async executePowerCheck(hardware: ActuatorHardwareSimulator): Promise<boolean> {
    this.transitionTo(ActuatorState.CHECKING_POWER);
    return await hardware.checkPower();
  }

  /**
   * Фаза 2: Розтискання гальма.
   */
  public async executeReleaseBrake(hardware: ActuatorHardwareSimulator, delayMs = 25): Promise<void> {
    this.transitionTo(ActuatorState.RELEASING_BRAKE);
    await hardware.releaseBrake();
    // Час на фізичне спрацьовування котушки електромагніту гальма
    await this.delay(delayMs);
  }

  /**
   * Фаза 3: Подача тяги мотора.
   */
  public async executeApplyTorque(
    hardware: ActuatorHardwareSimulator,
    currentPos: number,
    targetPos: number
  ): Promise<void> {
    this.transitionTo(ActuatorState.APPLYING_TORQUE);
    const direction = targetPos >= currentPos ? 'FORWARD' : 'REVERSE';
    await hardware.setMotorPower(100, direction);
  }

  /**
   * Фаза 4: Позначення активної фази руху.
   */
  public markMoving(): void {
    this.transitionTo(ActuatorState.MOVING);
  }

  /**
   * Фаза 5: Верифікація позиції після зняття тяги.
   */
  public async executeVerifyPosition(
    hardware: ActuatorHardwareSimulator,
    targetPos: Percentage,
    tolerancePct = 1.0
  ): Promise<{ inTolerance: boolean; actualPos: Percentage }> {
    this.transitionTo(ActuatorState.VERIFYING_POSITION);
    await hardware.cutMotorPower();

    const telemetry = await hardware.readTelemetry();
    const actualPos = new Percentage(telemetry.positionPct);
    const inTolerance = actualPos.equals(targetPos, tolerancePct);

    return { inTolerance, actualPos };
  }

  /**
   * Фаза 6: Затискання стопорного гальма.
   */
  public async executeEngageBrake(hardware: ActuatorHardwareSimulator, delayMs = 25): Promise<void> {
    this.transitionTo(ActuatorState.ENGAGING_BRAKE);
    await hardware.engageBrake();
    // Час на механічне притискання колодок пружиною
    await this.delay(delayMs);
  }

  /**
   * Фаза 7: Фіксація в режимі утримання (HOLDING).
   */
  public markHolding(): void {
    this.transitionTo(ActuatorState.HOLDING);
  }

  public markFailSafe(): void {
    this.transitionTo(ActuatorState.FAIL_SAFE);
  }

  public markInterlocked(): void {
    this.transitionTo(ActuatorState.INTERLOCKED);
  }

  public reset(): void {
    this.currentState = ActuatorState.IDLE;
    this.stateHistory.length = 0;
    this.transitionTo(ActuatorState.IDLE);
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
