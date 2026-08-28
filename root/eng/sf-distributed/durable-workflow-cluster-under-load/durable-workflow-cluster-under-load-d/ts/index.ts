import { condition, defineSignal, setHandler, continueAsNew } from '@temporalio/workflow';

export async function billingAccountWorkflow(state: AccountState): Promise<void> {
  let eventCount = 0;
  const depositSignal = defineSignal<[number]>('Deposit');

  setHandler(depositSignal, (amount) => {
    state.balance += amount;
    eventCount++;
  });

  while (true) {
    await condition(() => eventCount > 0);
    eventCount = 0;

    if (state.totalProcessedSignals >= 1000) {
      // Атомарний перезапуск із чистим журналом подій
      await continueAsNew<typeof billingAccountWorkflow>(state);
    }
  }
}
