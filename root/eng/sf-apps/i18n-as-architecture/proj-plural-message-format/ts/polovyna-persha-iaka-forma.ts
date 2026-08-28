const uk = new Intl.PluralRules("uk");

uk.resolvedOptions().pluralCategories;
// [ 'one', 'few', 'many', 'other' ]  — які гілки взагалі потрібні цій мові

[1, 2, 5, 11, 21, 1.5].map(n => `${n}→${uk.select(n)}`);
// [ '1→one', '2→few', '5→many', '11→many', '21→one', '1.5→other' ]

new Intl.NumberFormat("uk").format(1234.5);   // '1 234,5'
new Intl.NumberFormat("en").format(1234.5);   // '1,234.5'
