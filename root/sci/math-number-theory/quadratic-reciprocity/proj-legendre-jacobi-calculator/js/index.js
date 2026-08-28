function jacobiSymbol(a, n) {
    if (n <= 0 || n % 2 === 0) return 0;
    a = a % n;
    let t = 1;
    while (a !== 0) {
        while (a % 2 === 0) {
            a = Math.floor(a / 2);
            let r = n % 8;
            if (r === 3 || r === 5) {
                t = -t;
            }
        }
        let temp = a;
        a = n;
        n = temp;
        if (a % 4 === 3 && n % 4 === 3) {
            t = -t;
        }
        a = a % n;
    }
    if (n === 1) return t;
    return 0;
}
console.log("Символ Якобі (29 / 53):", jacobiSymbol(29, 53));
