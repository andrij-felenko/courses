const seamV = new HybridSeam(privateKey, publicKey, new MemoryStore(), 120, clock);
NOW = 0;                                              // назад на старт: логін від t=0 → exp = 0 + 120
let { access, refreshId } = await seamV.login(alice); // access живе 2 хв

NOW = 10;   console.log(await seamV.validate(access));  // → Principal   ЖИВА
            await seamV.revoke(refreshId);              //   ← «викинули телефон»: рвемо refresh
NOW = 11;   console.log(await seamV.validate(access));  // → Principal   access ще НЕ протух
NOW = 60;   console.log(await seamV.validate(access));  // → Principal   у межах 2-хв повідка
NOW = 121;  console.log(await seamV.validate(access));  // → null        access протух САМ
            console.log(await seamV.refresh(refreshId)); // → null       а нового не дадуть
