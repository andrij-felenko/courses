switch (state) {
    case A: {                // фігурні дужки роблять окремий блок
        int x = compute();   // x живе тільки тут — стрибнути повз нього не можна
        use(x);
        break;
    }
    case B:
        do_b();
        break;
}
