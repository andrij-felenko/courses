(*
    Функціональний блок: FB_EDM_Monitor
    Опис: Здійснює моніторинг зворотного зв'язку (External Device Monitoring) силових контакторів
          через їхні розмикальні (NC) допоміжні контакти. Забезпечує виявлення заклинювання
          або приварювання контактів за допомогою таймера контролю допустимої затримки перемикання.
*)
FUNCTION_BLOCK FB_EDM_Monitor
VAR_INPUT
    bControlOutput : BOOL;          (* Сигнал керування силових виходів (TRUE = увімкнено, FALSE = вимкнено) *)
    bFeedbackNC    : BOOL;          (* Сигнал з розмикальних (NC) допоміжних контактів контактора *)
    bReset         : BOOL;          (* Сигнал скидання помилки EDM *)
    stConfig       : ST_EdmConfig;  (* Конфігурація таймаутів моніторингу *)
END_VAR
VAR_OUTPUT
    bEdmOk         : BOOL := FALSE; (* Прапор норми: TRUE = ланцюг зворотного зв'язку у належному стані *)
    bError         : BOOL := FALSE; (* Прапор фіксації апаратної помилки контакторів *)
    eFaultState    : E_EdmFaultState := E_EdmFaultState.EDM_FAULT_NONE; (* Тип діагностованої помилки *)
END_VAR
VAR
    timerDelay     : TON;           (* Таймер затримки перемикання контактів *)
    bMismatch      : BOOL;          (* Прапор розбіжності між командою та зворотним зв'язком *)
END_VAR

(*
    Логіка моніторингу:
    У стабільному стані стан NC-контакту має бути протилежним команді керування:
    - Якщо bControlOutput = FALSE (контактор знеструмлено), NC-контакт має замкнутися (bFeedbackNC = TRUE).
    - Якщо bControlOutput = TRUE (контактор під напругою), NC-контакт має розімкнутися (bFeedbackNC = FALSE).
    Якщо bControlOutput = bFeedbackNC, виникає невідповідність (bMismatch = TRUE).
*)
bMismatch := (bControlOutput = bFeedbackNC);

(* Запуск таймера перевірки затримки спрацьовування *)
timerDelay(IN := bMismatch AND NOT bError, PT := stConfig.tFeedbackTimeout);

(* Фіксація помилки у разі перевищення таймауту *)
IF timerDelay.Q THEN
    bError := TRUE;
    IF NOT bControlOutput AND NOT bFeedbackNC THEN
        (* Вихід вимкнено, але NC-контакт не замкнувся -> приварювання силових контактів *)
        eFaultState := E_EdmFaultState.EDM_FAULT_CONTACT_WELDED;
    ELSIF bControlOutput AND bFeedbackNC THEN
        (* Вихід увімкнено, але NC-контакт не розімкнувся -> заклинювання у розімкненому стані *)
        eFaultState := E_EdmFaultState.EDM_FAULT_CONTACT_STUCK_OPEN;
    ELSE
        eFaultState := E_EdmFaultState.EDM_FAULT_TIMEOUT;
    END_IF;
END_IF;

(* Обробка процедури скидання помилки *)
IF bReset THEN
    (* Скидання дозволено лише якщо команду вимкнено і NC-контакт дійсно відновлено (замкнено) *)
    IF NOT bControlOutput AND bFeedbackNC THEN
        bError := FALSE;
        eFaultState := E_EdmFaultState.EDM_FAULT_NONE;
    END_IF;
END_IF;

(* Формування підсумкового прапорця стану EDM *)
bEdmOk := NOT bError AND NOT timerDelay.Q AND NOT bMismatch;

END_FUNCTION_BLOCK
