import { fromEvent } from "rxjs";
import { map, filter, debounceTime, distinctUntilChanged, switchMap, tap, catchError } from "rxjs/operators";

const search$ = fromEvent<InputEvent>(inputElement, "input").pipe(
  map(e => (e.target as HTMLInputElement).value.trim()),
  filter(text => text.length > 0),
  debounceTime(300),
  distinctUntilChanged(),
  tap(() => renderLoader(true)),
  switchMap(query => 
    fetchSearch(query).pipe(
      catchError(err => {
        handleError(err);
        return of([]);
      })
    )
  ),
  tap(() => renderLoader(false))
);

const subscription = search$.subscribe(results => renderResults(results));
// При закритті екрана: subscription.unsubscribe();
