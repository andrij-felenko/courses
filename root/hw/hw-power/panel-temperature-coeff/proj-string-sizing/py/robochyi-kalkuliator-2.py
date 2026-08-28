if __name__ == "__main__":
    panel = Panel(voc=41.0, vmpp=34.2, pmax=400.0,
                  b_voc=-0.29, b_vmpp=-0.34, g_pmax=-0.35, noct=45.0)
    inv = Inverter(v_max=600.0, v_mppt_min=150.0)
    site = Site(t_air_cold=-25.0, t_air_hot=40.0)

    r = size_string(panel, inv, site)
    n_naive = floor(inv.v_max / panel.voc)      # ПАСТКА: рахунок за STC

    print(f"холодний бік:  елемент {r['t_cold']:+.0f} °C, "
          f"Voc = {r['voc_cold']:.1f} В  →  max {r['n_max']} панелей")
    print(f"гарячий бік:   елемент {r['t_hot']:+.0f} °C, "
          f"Vmpp = {r['vmpp_hot']:.1f} В  →  min {r['n_min']} панелей")
    print(f"вікно рядка:   {r['n_min']} … {r['n_max']} панелей")
    print(f"Pmax на спеці: {r['pmax_hot']:.0f} Вт/панель  (−{r['loss_pct']:.0f} %)")
    print(f"якби за STC:   помилково дозволив би {n_naive} панелей "
          f"(на {n_naive - r['n_max']} більше — взимку це пробій)")

    n = r["n_max"] - 1                          # на панель нижче стелі — запас
    print(f"\nвибір {n} панелей у рядку:")
    print(f"  холодна Voc рядка = {n * r['voc_cold']:.0f} В  (стеля {inv.v_max:.0f} В)")
    print(f"  гаряча Vmpp рядка = {n * r['vmpp_hot']:.0f} В  (підлога {inv.v_mppt_min:.0f} В)")
    print(f"  потужність на спеці = {n * r['pmax_hot']:.0f} Вт  (STC {n * panel.pmax:.0f} Вт)")
