TYPE E_SafetyState :
(
    STATE_SAFE := 0,               (* Безпечний робочий стан, силові виходи увімкнені *)
    STATE_ESTOP_ACTIVE := 1,        (* Натиснуто кнопку аварійної зупинки E-Stop (канали розімкнені) *)
    STATE_WAITING_FOR_RESET := 2,    (* Входи відновлено, очікується ручне підтвердження (Reset) *)
    STATE_DISCREPANCY_FAULT := 3,   (* Апаратна помилка: перевищено час розбіжності між каналами *)
    STATE_EDM_FAULT := 4            (* Апаратна помилка: несправність контактора або приварювання контактів *)
);
END_TYPE

TYPE E_EStopFault :
(
    ESTOP_FAULT_NONE := 0,                 (* Помилки відсутні *)
    ESTOP_FAULT_DISCREPANCY_TIMEOUT := 1,   (* Перевищення часу розбіжності спрацьовування каналів *)
    ESTOP_FAULT_EDM := 2,                   (* Несправність ланцюга зворотного зв'язку EDM *)
    ESTOP_FAULT_INVALID_RESET := 3          (* Некоректна послідовність скидання *)
);
END_TYPE

TYPE E_EdmFaultState :
(
    EDM_FAULT_NONE := 0,                (* Ланцюг зворотного зв'язку справний *)
    EDM_FAULT_CONTACT_WELDED := 1,      (* Приварювання контактів (NC не замкнувся при вимкненні) *)
    EDM_FAULT_CONTACT_STUCK_OPEN := 2,  (* Заклинювання реле (NC не розімкнувся при увімкненні) *)
    EDM_FAULT_TIMEOUT := 3              (* Таймаут підтвердження стану контакторів *)
);
END_TYPE

TYPE ST_EdmConfig :
STRUCT
    tFeedbackTimeout : TIME := T#250ms; (* Максимальний час очікування відповіді зворотного зв'язку *)
END_STRUCT
END_TYPE

TYPE ST_EStopConfig :
STRUCT
    tDiscrepancyTime : TIME := T#100ms; (* Допустима часова розбіжність між каналами E-Stop *)
    stEdmConfig      : ST_EdmConfig;    (* Конфігурація моніторингу зворотного зв'язку *)
END_STRUCT
END_TYPE
