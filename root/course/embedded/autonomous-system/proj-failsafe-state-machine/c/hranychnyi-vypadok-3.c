switch (current) {
    case MODE_AUTO:   run_auto();   break;
    case MODE_LOITER: run_loiter(); break;
    case MODE_RTL:    run_rtl();    break;
    case MODE_LAND:   run_land();   break;
    default:
        // невідомий режим = зіпсований стан. НЕ довіряй, сідай.
        current = MODE_LAND;
        run_land();
        log_error("FSM: невідомий режим, аварійна посадка");
        break;
}
