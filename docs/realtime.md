## Generating Backfill Data for Batch and Real-time data in a Stream
It is often the case that older data is needed to backfill history up until now and then begin streaming data.
It can be hard to align where the batch file ends and where the streaming begins.

It can be done by using two simulations of the same generator specification with the following two job specs:

Batch File Generation example using the `iot/iot_twin.json` specification:
```json
{
  "name": "generate_6_months_iot"
  "type": "replay",
  "target": {
    "type": "file",
    "path": "iot-6-month.json"
  },
  "config": "iot/iot_twin.json",
  "time_type": "2023-04-01 00:00:00",
  "time": "4392h",
  "concurrency": 1
}
```
Assuming that you want 6 months up until now, and today is Oct 1st 2023.
- We go back 6 months and start the simulation at "time_type":"2023-04-01 00:00:00".
- There are 183 days in that period, but we can only use hours, so that's "time":"4392h"
- "concurrency":1 replay jobs do not need to simulated multiple entities, the entities are already represented in the source file so we only need one thread. 
- Notice that this job uses a target file which will then presumably be loaded through a batch ingestion.

The job will generate events that start on April 1st 2023 and end on October 1st 2023 at 00:00:00.
So the stream needs to pick up from there. 

The stream job will pick up where the batch file ended using the "time_type" set to the end of the batch. In this case "2023-10-01 00:00:00"
Given that the simulation will start slighly in the past, it will catchup to now be generating events from the start time to the current time and then continue to run in real-time.
Streaming example using the iot/iot_twin.json to continue from the batch:
```json
{
  "name": "generate_6_months_iot"
  "type": "replay",
  "target": {
    "type": "kafka",
    "endpoint": "kafka:9092",
    "topic": "iot"
  },
  "config": "iot/iot_twin.json",
  "time_type": "2023-10-01 00:00:00",
  "time": "24h",
  "concurrency": 1
}
```

Note that this job is set to run for 24 hours, that is 24 hours from the simulated start. So if the simulation starts at "2023-10-01 00:00:00" and it is currently 8am, you can use "time":"24h". It will catch up very quickly to the current time, emitting all the events into the stream from midnight until 8 am and then continue with normal event cadence for another 16 hours.