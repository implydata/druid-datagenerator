## Emitter dimension cardinality

Many dimension types may include a _Cardinality_ (the one exception is the _enum_ dimension type).
Cardinality defines how many unique values the driver may generate.
Setting _cardinality_ to 0 provides no constraint to the number of unique values.
But, setting _cardinality_ > 0 causes the driver to create a list of values, and the length of the list is the value of _cardinality_.

When _cardinality_ is greater than 0, <i>cardinality_distribution</i> informs how the driver selects items from the cardinality list.
We can think of the cardinality list as a list with zero-based indexing, and the <i>cardinality_distribution</i> determines how the driver will select an index into the cardinality list.
After using the <i>cardinality_distribution</i> to produce an index, the driver constrains the index so as to be a valid value (i.e., 0 <= index < length of cardinality list).
Note that while _uniform_ and _normal_ distributions make sense to use as distribution specifications, _constant_ distributions only make sense if the cardinality list contains only a single value.
Further, for cardinality > 0, avoid an _exponential_ distribution as it will round down any values that are too large and produces a distorted distribution.

As an example of cardinality, imagine the following String element definition:

```
{
  "type": "string",
  "name": "Str1",
  "length_distribution": {"type": "uniform", "min": 3, "max": 6},
  "cardinality": 5,
  "cardinality_distribution": {"type": "uniform", "min": 0, "max": 4},
  "chars": "abcdefg"
}
```

This defines a String element named Str1 with five unique values that are three to six characters in length.
The driver will select from these five unique values uniformly (by selecting indices in the range of [0,4]).
All values may only consist of strings containing the letters a-g.
