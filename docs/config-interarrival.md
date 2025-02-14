## Event interarrival time

`interarrival` sets the inter-arrival time in seconds between events emitted by the data generator, described using a [distribution](#distributions.md).

The following example sets a `constant` distribution descriptor so that events are spaced one second apart.


```
{
:
  "interarrival": {
    "type": "constant",
    "value": 1
  },
:
}
```

The mean inter-arrival time is the division of a period of time by the number of records to generate during the time period. For example, 100 records per hour has an inter-arrival time of 36 seconds per record (1 hour * 60 minutes/hour * 60 seconds/minute / 100 records).