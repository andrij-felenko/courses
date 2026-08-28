import { useEffect, useMemo, useRef } from 'react';

export function useDebouncedCallback<TArgs extends any[]>(
  callback: (...args: TArgs) => void,
  delay: number
) {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  const debounced = useMemo(
    () => debounce((...args: TArgs) => callbackRef.current(...args), delay),
    [delay]
  );

  useEffect(() => {
    // Гарантоване скасування таймера при демонтажі компонента
    return () => debounced.cancel();
  }, [debounced]);

  return debounced;
}
