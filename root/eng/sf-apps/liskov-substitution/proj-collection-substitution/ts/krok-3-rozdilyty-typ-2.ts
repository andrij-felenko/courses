// fill вимагає рівно свою потребу — можливість додавати.
function fill(list: MutableList<number>, n: number): void {
  for (let i = 0; i < n; i++) list.add(i);
}

fill(new ArrayList<number>(), 3);       // ок

const frozen = new ImmutableList<number>([10, 20]);
fill(frozen, 3);
//   ^^^^^^ Argument of type 'ImmutableList<number>' is not
//          assignable to parameter of type 'MutableList<number>'.
//          Property 'add' is missing in type 'ImmutableList<number>'.
