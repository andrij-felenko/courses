public final class Flow {
    public interface Publisher<T> {
        void subscribe(Subscriber<? super T> subscriber);
    }
    public interface Subscriber<T> {
        void onSubscribe(Subscription subscription);
        void onNext(T item);
        void onError(Throwable throwable);
        void onComplete();
    }
    public interface Subscription {
        void request(long n);   // той самий зворотний попит
        void cancel();
    }
    public interface Processor<T,R> extends Subscriber<T>, Publisher<R> {}
}
