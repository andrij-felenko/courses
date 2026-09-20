/**
 * Вихідний шлюзовий адаптер (ActuatorGatewayAdapter).
 * Реалізує доменний вихідний порт ActuatorOutboundPort.
 * Оркеструє роботу скінченного автомата секвенсера, монітора телеметрії
 * та контролера безпеки. Транслює декларативні доменні команди у низькорівневі
 * протокольні виклики та мапить будь-які технічні помилки у доменний звіт ActuatorExecutionReport,
 * не дозволяючи виняткам протікати в ядро застосунку.
 */
import { ActuatorHardwareSimulator } from './hardware-simulator.ts';
import { ActuatorSequencerFsm } from './actuator-sequencer-fsm.ts';
import { TelemetryMonitor } from './telemetry-monitor.ts';
import { FailSafeController } from './fail-safe-controller.ts';
import {
  ActuatorErrorCode,
  ActuatorExecutionReport,
  ActuatorId,
  ActuatorOutboundPort,
  ActuatorState,
  Percentage,
  SetPositionCommand,
  CallContext
} from './types.ts';

export class ActuatorGatewayAdapter implements ActuatorOutboundPort {
  private readonly hardware: ActuatorHardwareSimulator;
  private readonly sequencer: ActuatorSequencerFsm;
  private readonly telemetryMonitor: TelemetryMonitor;
  private readonly failSafeController: FailSafeController;

  constructor(
    hardware: ActuatorHardwareSimulator,
    sequencer = new ActuatorSequencerFsm(),
    telemetryMonitor = new TelemetryMonitor(),
    failSafeController = new FailSafeController()
  ) {
    this.hardware = hardware;
    this.sequencer = sequencer;
    this.telemetryMonitor = telemetryMonitor;
    this.failSafeController = failSafeController;
  }

  /**
   * Головний метод трансляції та виконання доменної команди позиціонування.
   * Усі винятки низького рівня перехоплюються і конвертуються у типізований ActuatorExecutionReport.
   */
  public async execute(command: SetPositionCommand): Promise<ActuatorExecutionReport> {
    const startTime = Date.now();
    const targetPct = command.targetPosition;
    const context = command.context;

    // 0. Перевірка захисного блокування Safety Interlock
    if (this.failSafeController.isSafetyInterlocked()) {
      const reason = this.failSafeController.getInterlockReason() ?? 'Активовано захисне блокування Safety Interlock';
      return {
        success: false,
        actuatorId: command.actuatorId,
        requestedPosition: targetPct,
        actualPosition: await this.readCurrentPositionSafe(),
        durationMs: Date.now() - startTime,
        finalState: ActuatorState.INTERLOCKED,
        isSafetyInterlocked: true,
        error: {
          code: ActuatorErrorCode.COMMAND_REJECTED,
          message: `Команду відхилено: привід заблоковано через попередню аварію (${reason})`
        }
      };
    }

    this.sequencer.reset();
    this.telemetryMonitor.reset();

    try {
      // 1. Фаза перевірки живлення (CHECKING_POWER)
      this.checkDeadlineAndCancellation(context, startTime);
      const isPowerOk = await this.sequencer.executePowerCheck(this.hardware);
      if (!isPowerOk) {
        throw { code: ActuatorErrorCode.HARDWARE_FAULT, message: 'Збій живлення силової шини актуатора' };
      }

      // 2. Фаза розтискання стопорного гальма (RELEASING_BRAKE)
      this.checkDeadlineAndCancellation(context, startTime);
      await this.sequencer.executeReleaseBrake(this.hardware);

      // 3. Зчитування поточної позиції перед рухом
      const initialTelemetry = await this.hardware.readTelemetry();
      const initialPos = initialTelemetry.positionPct;

      // 4. Фаза подачі тяги мотора (APPLYING_TORQUE)
      this.checkDeadlineAndCancellation(context, startTime);
      await this.sequencer.executeApplyTorque(this.hardware, initialPos, targetPct.value);

      // 5. Фаза переміщення з квантовим опитуванням (MOVING)
      this.sequencer.markMoving();
      await this.runMovementLoop(targetPct, context, startTime);

      // 6. Фаза перевірки фінальної позиції (VERIFYING_POSITION)
      const verifyResult = await this.sequencer.executeVerifyPosition(this.hardware, targetPct);
      if (!verifyResult.inTolerance) {
        throw {
          code: ActuatorErrorCode.MECHANICAL_STALL,
          message: `Позицію не досягнуто: фактично ${verifyResult.actualPos}, очікувалось ${targetPct}`
        };
      }

      // 7. Фаза фіксації гальмом (ENGAGING_BRAKE)
      await this.sequencer.executeEngageBrake(this.hardware);

      // 8. Перехід у режим спокійного утримання (HOLDING)
      this.sequencer.markHolding();

      const finalDuration = Date.now() - startTime;
      return {
        success: true,
        actuatorId: command.actuatorId,
        requestedPosition: targetPct,
        actualPosition: verifyResult.actualPos,
        durationMs: finalDuration,
        finalState: this.sequencer.getState(),
        isSafetyInterlocked: false
      };
    } catch (err: unknown) {
      // Перехоплення будь-якої технічної або логічної помилки: гарантований перехід у безпечний стан
      return await this.handleExecutionFailure(command, targetPct, startTime, err);
    }
  }

  /**
   * Неблокуючий цикл руху з квантовим опитуванням телеметрії та симуляцією фізики.
   */
  private async runMovementLoop(targetPct: Percentage, context: CallContext, startTime: number): Promise<void> {
    const quantumMs = this.telemetryMonitor.getQuantumMs();

    while (true) {
      this.checkDeadlineAndCancellation(context, startTime);

      // Квант часу фізичного світу
      this.hardware.simulateStep(quantumMs);

      // Опитування датчиків через монітор
      const pollResult = await this.telemetryMonitor.pollQuantum(this.hardware);

      // Перевірка на заклинювання
      if (pollResult.isStalled) {
        throw {
          code: ActuatorErrorCode.MECHANICAL_STALL,
          message: pollResult.stallReason ?? 'Виявлено механічне заклинювання вала приводу',
          snapshot: pollResult.telemetry
        };
      }

      // Перевірка досягнення цільової зони
      const currentPos = new Percentage(pollResult.telemetry.positionPct);
      if (currentPos.equals(targetPct, 0.8)) {
        break; // Цільову точку досягнуто в межах допуску
      }

      // Неблокуюча пауза на величину кванта часу
      await new Promise((resolve) => setTimeout(resolve, quantumMs));
    }
  }

  /**
   * Перевірка лімітів часу виконання (WCET) та прапорця скасування.
   */
  private checkDeadlineAndCancellation(context: CallContext, startTime: number): void {
    if (context.cancellationToken?.isCancelled) {
      throw {
        code: ActuatorErrorCode.COMMAND_REJECTED,
        message: 'Операцію перервано за запитом доменного скасування'
      };
    }

    const elapsed = Date.now() - startTime;
    if (elapsed > context.deadlineMs) {
      throw {
        code: ActuatorErrorCode.TIMEOUT_EXPIRED,
        message: `Перевищено граничний час операції (дедлайн ${context.deadlineMs} мс, минуло ${elapsed} мс)`
      };
    }
  }

  /**
   * Гарантована обробка аварії: виклик контролера безпеки та побудова типізованого звіту.
   */
  private async handleExecutionFailure(
    command: SetPositionCommand,
    targetPct: Percentage,
    startTime: number,
    err: unknown
  ): Promise<ActuatorExecutionReport> {
    this.sequencer.markFailSafe();

    let errorCode = ActuatorErrorCode.HARDWARE_FAULT;
    let message = 'Непередбачена апаратна несправність';
    let snapshot = this.telemetryMonitor.getLastSample() ?? undefined;

    if (typeof err === 'object' && err !== null) {
      const e = err as { code?: ActuatorErrorCode; message?: string; snapshot?: any };
      if (e.code) errorCode = e.code;
      if (e.message) message = e.message;
      if (e.snapshot) snapshot = e.snapshot;
    } else if (err instanceof Error) {
      message = err.message;
      if (err.message.includes('COMM_TIMEOUT')) {
        errorCode = ActuatorErrorCode.DEVICE_OFFLINE;
      }
    }

    // Запуск аварійного протоколу Fail-Safe
    const rollbackResult = await this.failSafeController.executeEmergencyRollback(
      this.hardware,
      message,
      errorCode
    );
    this.sequencer.markInterlocked();

    const actualPos = await this.readCurrentPositionSafe();
    const duration = Date.now() - startTime;

    return {
      success: false,
      actuatorId: command.actuatorId,
      requestedPosition: targetPct,
      actualPosition: actualPos,
      durationMs: duration,
      finalState: ActuatorState.INTERLOCKED,
      isSafetyInterlocked: rollbackResult.interlocked,
      error: {
        code: errorCode,
        message,
        telemetrySnapshot: rollbackResult.snapshot ?? snapshot
      }
    };
  }

  private async readCurrentPositionSafe(): Promise<Percentage> {
    try {
      const telemetry = await this.hardware.readTelemetry();
      return new Percentage(telemetry.positionPct);
    } catch {
      return new Percentage(0.0);
    }
  }

  /**
   * Екстрена зупинка за прямим викликом з ядра.
   */
  public async emergencyStop(actuatorId: ActuatorId, reason: string): Promise<ActuatorExecutionReport> {
    const startTime = Date.now();
    const rollback = await this.failSafeController.executeEmergencyRollback(
      this.hardware,
      reason,
      ActuatorErrorCode.COMMAND_REJECTED
    );
    this.sequencer.markInterlocked();
    const pos = await this.readCurrentPositionSafe();

    return {
      success: false,
      actuatorId,
      requestedPosition: pos,
      actualPosition: pos,
      durationMs: Date.now() - startTime,
      finalState: ActuatorState.INTERLOCKED,
      isSafetyInterlocked: true,
      error: {
        code: ActuatorErrorCode.COMMAND_REJECTED,
        message: `Аварійна зупинка: ${reason}`,
        telemetrySnapshot: rollback.snapshot ?? undefined
      }
    };
  }

  public async queryState(actuatorId: ActuatorId): Promise<{
    currentState: ActuatorState;
    position: Percentage;
    isInterlocked: boolean;
  }> {
    const pos = await this.readCurrentPositionSafe();
    return {
      currentState: this.sequencer.getState(),
      position: pos,
      isInterlocked: this.failSafeController.isSafetyInterlocked()
    };
  }

  public async resetSafetyInterlock(actuatorId: ActuatorId): Promise<boolean> {
    this.failSafeController.resetInterlock();
    this.sequencer.reset();
    this.hardware.clearFaults();
    return true;
  }
}
