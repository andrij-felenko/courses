(*
    Функціональний блок: FB_EStop
    Опис: Реалізує функціонал безпеки двоканального аварійного зупину (E-Stop) з перевіркою
          часової розбіжності входів (Discrepancy Time), інтегрованим моніторингом зворотного
          зв'язку силових реле (EDM) та детермінованим автоматом станів.
*)
FUNCTION_BLOCK FB_EStop
VAR_INPUT
    bChannel1      : BOOL;          (* Перший канал кнопки E-Stop (F-DI 1, NC) *)
    bChannel2      : BOOL;          (* Другий канал кнопки E-Stop (F-DI 2, NC) *)
    bFeedbackNC    : BOOL;          (* Зворотний зв'язок NC-контактів силових реле *)
    bReset         : BOOL;          (* Сигнал кнопки ручного підтвердження/скидання (Reset) *)
    stConfig       : ST_EStopConfig;(* Параметри затримок та конфігурація EDM *)
END_VAR
VAR_OUTPUT
    bSafetyOutput  : BOOL := FALSE; (* Вихід дозволу роботи силових ланцюгів (F-DO) *)
    bReadyForReset : BOOL := FALSE; (* Сигнал індикації готовності до скидання (очікування Reset) *)
    bError         : BOOL := FALSE; (* Прапор виявлення апаратної помилки *)
    eState         : E_SafetyState := E_SafetyState.STATE_ESTOP_ACTIVE; (* Поточний стан безпеки *)
    eFault         : E_EStopFault  := E_EStopFault.ESTOP_FAULT_NONE;    (* Поточна фіксована помилка *)
END_VAR
VAR
    fbEdm          : FB_EDM_Monitor;(* Екземпляр блоку моніторингу контакторів *)
    timerDiscrepancy: TON;          (* Таймер контролю часової розбіжності входів *)
    rTrigReset     : R_TRIG;        (* Визначник наростаючого фронту для сигналу Reset *)
END_VAR

(* Виявлення фронту сигналу скидання (захист від постійно затиснутої кнопки Reset) *)
rTrigReset(CLK := bReset);

(* Виклик підсистеми EDM моніторингу *)
fbEdm(
    bControlOutput := bSafetyOutput,
    bFeedbackNC    := bFeedbackNC,
    bReset         := bReset,
    stConfig       := stConfig.stEdmConfig
);

(* Таймер контролю часової розбіжності між двома каналами кнопки аварійної зупинки *)
timerDiscrepancy(
    IN := (bChannel1 <> bChannel2) AND (eState <> E_SafetyState.STATE_DISCREPANCY_FAULT),
    PT := stConfig.tDiscrepancyTime
);

(* Фіксація помилки часової розбіжності при перевищенні таймауту *)
IF timerDiscrepancy.Q THEN
    eState := E_SafetyState.STATE_DISCREPANCY_FAULT;
    eFault := E_EStopFault.ESTOP_FAULT_DISCREPANCY_TIMEOUT;
END_IF;

(* Обробка виникнення аварії у ланцюзі EDM *)
IF fbEdm.bError AND (eState <> E_SafetyState.STATE_DISCREPANCY_FAULT) THEN
    eState := E_SafetyState.STATE_EDM_FAULT;
    eFault := E_EStopFault.ESTOP_FAULT_EDM;
END_IF;

(* Автомат станів безпеки *)
CASE eState OF
    E_SafetyState.STATE_SAFE:
        bSafetyOutput := TRUE;
        bReadyForReset := FALSE;
        bError := FALSE;

        (* Реагування на зміну стану каналів E-Stop *)
        IF NOT bChannel1 OR NOT bChannel2 THEN
            bSafetyOutput := FALSE;
            IF NOT bChannel1 AND NOT bChannel2 THEN
                eState := E_SafetyState.STATE_ESTOP_ACTIVE;
            END_IF;
        END_IF;

    E_SafetyState.STATE_ESTOP_ACTIVE:
        bSafetyOutput := FALSE;
        bReadyForReset := FALSE;
        bError := FALSE;

        (* Перехід у стан очікування скидання після відновлення обох каналів *)
        IF bChannel1 AND bChannel2 THEN
            eState := E_SafetyState.STATE_WAITING_FOR_RESET;
        END_IF;

    E_SafetyState.STATE_WAITING_FOR_RESET:
        bSafetyOutput := FALSE;
        bReadyForReset := TRUE;
        bError := FALSE;

        (* Перевірка повторного розмикання входів E-Stop *)
        IF NOT bChannel1 OR NOT bChannel2 THEN
            bReadyForReset := FALSE;
            IF NOT bChannel1 AND NOT bChannel2 THEN
                eState := E_SafetyState.STATE_ESTOP_ACTIVE;
            END_IF;
        (* Ручне скидання за допомогою фронту сигналу Reset *)
        ELSIF rTrigReset.Q THEN
            IF fbEdm.bEdmOk THEN
                eState := E_SafetyState.STATE_SAFE;
                eFault := E_EStopFault.ESTOP_FAULT_NONE;
            ELSE
                eState := E_SafetyState.STATE_EDM_FAULT;
                eFault := E_EStopFault.ESTOP_FAULT_EDM;
            END_IF;
        END_IF;

    E_SafetyState.STATE_DISCREPANCY_FAULT:
        bSafetyOutput := FALSE;
        bReadyForReset := FALSE;
        bError := TRUE;

        (* Квитування помилки розбіжності можливе лише після повного натискання кнопки E-Stop (обидва канали FALSE) *)
        IF NOT bChannel1 AND NOT bChannel2 THEN
            eState := E_SafetyState.STATE_ESTOP_ACTIVE;
        END_IF;

    E_SafetyState.STATE_EDM_FAULT:
        bSafetyOutput := FALSE;
        bReadyForReset := FALSE;
        bError := TRUE;

        (* Спроба відновлення роботи при натисканні Reset, якщо контактори справні *)
        IF rTrigReset.Q THEN
            IF NOT fbEdm.bError AND bChannel1 AND bChannel2 THEN
                eState := E_SafetyState.STATE_WAITING_FOR_RESET;
                eFault := E_EStopFault.ESTOP_FAULT_NONE;
            END_IF;
        END_IF;
END_CASE;

END_FUNCTION_BLOCK
