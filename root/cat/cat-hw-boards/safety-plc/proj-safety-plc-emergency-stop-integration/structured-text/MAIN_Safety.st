(*
    Програма: MAIN_Safety
    Опис: Головна циклічна програма (Safety PRG) для програмованого логічного контролера
          безпеки (Safety PLC). Здійснює опитування безпечних входів F-DI, викликає
          функціональний блок E-Stop та керує виходами безпеки F-DO і світлосигнальною арматурою.
*)
PROGRAM MAIN_Safety
VAR
    (* Фізичні / логічні входи безпеки (F-DI - Safe Digital Inputs) *)
    i_bEStop_Ch1     : BOOL := TRUE;  (* Вхід каналу 1 грибка аварійної зупинки *)
    i_bEStop_Ch2     : BOOL := TRUE;  (* Вхід каналу 2 грибка аварійної зупинки *)
    i_bContactor_NC  : BOOL := TRUE;  (* Зворотний зв'язок NC-контактів силових реле *)
    i_bResetButton   : BOOL := FALSE; (* Сигнал кнопки ручного підтвердження/скидання *)

    (* Фізичні / логічні виходи безпеки (F-DO - Safe Digital Outputs) *)
    q_bSafetyEnable  : BOOL := FALSE; (* Вихід дозволу живлення силових приводів *)
    q_bResetLamp     : BOOL := FALSE; (* Світловий індикатор кнопки Reset (очікування підтвердження) *)
    q_bFaultLamp     : BOOL := FALSE; (* Світловий індикатор аварії / несправності *)

    (* Екземпляр функціонального блоку логіки безпеки *)
    fbEStopLogic     : FB_EStop;

    (* Конфігурація параметрів затримок *)
    stSafetyConfig   : ST_EStopConfig;

    (* Прапор первинної ініціалізації *)
    bInitialised     : BOOL := FALSE;
END_VAR

(* Первинне встановлення параметрів у першому циклі *)
IF NOT bInitialised THEN
    stSafetyConfig.tDiscrepancyTime := T#100ms;
    stSafetyConfig.stEdmConfig.tFeedbackTimeout := T#250ms;
    bInitialised := TRUE;
END_IF;

(* Цикличне виконання логіки безпечного аварійного зупину *)
fbEStopLogic(
    bChannel1   := i_bEStop_Ch1,
    bChannel2   := i_bEStop_Ch2,
    bFeedbackNC := i_bContactor_NC,
    bReset      := i_bResetButton,
    stConfig    := stSafetyConfig
);

(* Запис результатів у виходи безпеки F-DO *)
q_bSafetyEnable := fbEStopLogic.bSafetyOutput;
q_bResetLamp    := fbEStopLogic.bReadyForReset;
q_bFaultLamp    := fbEStopLogic.bError;

END_PROGRAM
