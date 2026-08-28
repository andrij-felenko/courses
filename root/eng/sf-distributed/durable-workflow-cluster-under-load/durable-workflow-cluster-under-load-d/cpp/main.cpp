// C++ SDK: виклик Continue-As-New через контекстний метод
class BillingAccountWorkflow {
public:
    void run(WorkflowContext& ctx, AccountState state) {
        int event_count = 0;
        
        while (true) {
            auto signal = ctx.wait_for_signal<DepositSignal>("Deposit");
            state.balance += signal.amount;
            event_count++;

            if (event_count >= 1000) {
                // Атомарна передача знімка стану в новий запуск
                ctx.continue_as_new("BillingAccountWorkflow", ContinueAsNewOptions{}, state);
            }
        }
    }
};
