export interface SingleFlightResult<T> {
    value: T;
    shared: boolean;
}

export class SingleFlightGroup {
    private inFlight = new Map<string, Promise<any>>();

    async do<T>(key: string, fn: () => Promise<T>): Promise<SingleFlightResult<T>> {
        const existing = this.inFlight.get(key);
        if (existing) {
            const value = await existing;
            return { value, shared: true };
        }

        const promise = (async () => {
            try {
                return await fn();
            } finally {
                this.inFlight.delete(key);
            }
        })();

        this.inFlight.set(key, promise);
        const value = await promise;
        return { value, shared: false };
    }
}
