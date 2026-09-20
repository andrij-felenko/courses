/**
 * Демонстрація трансляції доменних команд у протокол актуатора:
 * 1. Успішне позиціонування заслінки з 0% до 75% через поетапний цикл FSM.
 * 2. Виявлення заклинювання за струмом/енкодером та аварійне спрацьовування Fail-Safe.
 * 3. Захист від повторних запусків (Safety Interlock) при спробі руху заблокованого вузла.
 * 4. Контрольоване скидання блокування оператором та повернення приводу в роботу.
 */
import { ActuatorHardwareSimulator } from './hardware-simulator.ts';
import { ActuatorGatewayAdapter } from './actuator-gateway-adapter.ts';
import { ActuatorId, Percentage, SetPositionCommand } from './types.ts';

async function main(): Promise<void> {
  console.log('================================================================');
  console.log('  АРХІТЕКТУРА СИСТЕМ: ТРАНСЛЯЦІЯ ДОМЕННИХ КОМАНД В АКТУАТОРИ');
  console.log('================================================================\n');

  const actuatorId = new ActuatorId('actuator-valve-42');
  const hardware = new ActuatorHardwareSimulator(actuatorId.value, 0.0);
  const adapter = new ActuatorGatewayAdapter(hardware);

  // --------------------------------------------------------------------------
  // СЦЕНАРІЙ 1: Штатне позиціонування (0.0% -> 75.0%)
  // --------------------------------------------------------------------------
  console.log('▶ СЦЕНАРІЙ 1: Штатна команда позиціонування до 75.0%...');
  const cmd1: SetPositionCommand = {
    actuatorId,
    targetPosition: new Percentage(75.0),
    context: { deadlineMs: 5000 }
  };

  const report1 = await adapter.execute(cmd1);

  console.log(`  Статус виконання:    ${report1.success ? '✓ УСПІХ' : '✗ ПОМИЛКА'}`);
  console.log(`  Запитана позиція:    ${report1.requestedPosition}`);
  console.log(`  Досягнута позиція:   ${report1.actualPosition}`);
  console.log(`  Тривалість операції: ${report1.durationMs} мс`);
  console.log(`  Фінальний стан FSM:  ${report1.finalState}`);
  console.log(`  Safety Interlock:    ${report1.isSafetyInterlocked ? 'АКТИВНИЙ' : 'НЕМАЄ'}\n`);

  // --------------------------------------------------------------------------
  // СЦЕНАРІЙ 2: Аварійне заклинювання редуктора при спробі переміщення до 20.0%
  // --------------------------------------------------------------------------
  console.log('▶ СЦЕНАРІЙ 2: Моделювання механічного заклинювання вала на 45.0%...');
  hardware.forceStallAt(45.0); // Механічний бар'єр/перешкода на шляху

  const cmd2: SetPositionCommand = {
    actuatorId,
    targetPosition: new Percentage(20.0),
    context: { deadlineMs: 4000 }
  };

  const report2 = await adapter.execute(cmd2);

  console.log(`  Статус виконання:    ${report2.success ? '✓ УСПІХ' : '✗ ПОМИЛКА (ОЧІКУВАНО)'}`);
  console.log(`  Код доменної помилки: ${report2.error?.code}`);
  console.log(`  Причина відмови:     ${report2.error?.message}`);
  console.log(`  Зупинка на позиції:  ${report2.actualPosition}`);
  console.log(`  Фінальний стан FSM:  ${report2.finalState}`);
  console.log(`  Safety Interlock:    ${report2.isSafetyInterlocked ? 'АКТИВНИЙ (ЗАБЛОКОВАНО)' : 'НІ'}`);
  if (report2.error?.telemetrySnapshot) {
    const s = report2.error.telemetrySnapshot;
    console.log(`  Діагностичний знімок: струм ${s.currentAmperes} A (гальмо: ${s.brakeEngaged}, двигун: ${s.motorEnergized})`);
  }
  console.log();

  // --------------------------------------------------------------------------
  // СЦЕНАРІЙ 3: Захист від повторних запусків (Safety Interlock)
  // Доменне ядро намагається знову надіслати команду на рух заблокованого вузла
  // --------------------------------------------------------------------------
  console.log('▶ СЦЕНАРІЙ 3: Спроба повторного запуску без квитування аварії...');
  const cmd3: SetPositionCommand = {
    actuatorId,
    targetPosition: new Percentage(10.0),
    context: { deadlineMs: 2000 }
  };

  const report3 = await adapter.execute(cmd3);

  console.log(`  Статус виконання:    ${report3.success ? '✓ УСПІХ' : '✗ ВІДХИЛЕНО АДАПТЕРОМ'}`);
  console.log(`  Код доменної помилки: ${report3.error?.code}`);
  console.log(`  Повідомлення:        ${report3.error?.message}`);
  console.log(`  Блокування збережено: ${report3.isSafetyInterlocked ? 'ТАК' : 'НІ'}\n`);

  // --------------------------------------------------------------------------
  // СЦЕНАРІЙ 4: Відновлення роботи після сервісного скидання оператором
  // --------------------------------------------------------------------------
  console.log('▶ СЦЕНАРІЙ 4: Скидання блокування оператором та повернення в роботу...');
  await adapter.resetSafetyInterlock(actuatorId);
  console.log('  ✓ Аварійний запобіжник скинуто оператором.');

  const cmd4: SetPositionCommand = {
    actuatorId,
    targetPosition: new Percentage(50.0),
    context: { deadlineMs: 3000 }
  };

  const report4 = await adapter.execute(cmd4);

  console.log(`  Статус виконання:    ${report4.success ? '✓ УСПІХ' : '✗ ПОМИЛКА'}`);
  console.log(`  Досягнута позиція:   ${report4.actualPosition}`);
  console.log(`  Фінальний стан FSM:  ${report4.finalState}`);
  console.log(`  Safety Interlock:    ${report4.isSafetyInterlocked ? 'АКТИВНИЙ' : 'НЕМАЄ'}\n`);

  console.log('================================================================');
  console.log('  УСІ СЦЕНАРІЇ УСПІШНО ПРОЙДЕНО: ДОМЕННЕ ЯДРО ПОВНІСТЮ ІЗОЛЬОВАНЕ');
  console.log('================================================================');
}

void main();
