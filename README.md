# How to use the Druid Data Driver


## The Data Driver Server using Docker
You can run the data driver in a docker container using:
```
docker run -d -p 9999:9999 imply/datagen:latest
```

The server provides the following APIs:

### list
Lists the data generation configurations available on the server.
Example:
```
curl "http://localhost:9999/list"
```
Output: 
```
["clickstream/clickstream.json", "clickstream/users_init.json", "clickstream/users_changes.json", "examples/langmap.json", "examples/missing.json", "examples/simple.json", "examples/list.json", "examples/deepthought.json", "examples/variable.json", "examples/nulls.json", "examples/counter.json", "examples/object.json", "examples/types.json"]
```

### /start
Initiates a data generation process with the specified configuration. The configuration can be selected from the available configurations by using the `config_file` property in the request. Alternatively, a custom configuration can be provided in the `config` property.
The payload for this request has the following format:
```json
{
    "name": "<job name>",
    "target": "<target specification>",
    "config": "<config JSON>",
    "config_file": "<name of the config file on the server>",
    "total_events": "<total number of messages to generate>",
    "concurrency": "<max number of concurrent state machines>",
    "time": "<duration for data generation>",
    "time_type": "SIM | REAL | <start timestamp>"
}
```
Where:
- _"name"_ - (required) unique name for the job
- _"target"_ - (required) describes where to publish generated data.
- _"config"_ - (_config_ or _config_file_ required) custom configuration object.
- _"config_file"_ - (_config_ or _config_file_ required) [predefined configuration](###GET_/list) is used.
- _"total_events"_ - (optional) total number of events to generate
- _"time"_ - (optional) total duration to run specified in seconds, minutes or hours (ex. "15s", "10m", "5h")
- _"concurrency"_ - (optional) max number of state machines to create
- _"time_type"_ - (optional) "SIM" - simulate time, "REAL" - run in real-time
  - can be set to a timestamp ("YYYY-MM-DD HH:MM:SS") to use a simulated start time  

When "time_type" is either "SIM" or a timestamp literal value, the job will simulate the passage of time for a with a simulated duration of "time" and complete when the simulated duration is reached.

If "time_type" is "REAL" then and "time" is specified, then the job will complete after the specified duration in real time.

If "total_events" is specified, the job will complete once it generates the specified number of messages.

Example payload:
```json
{
    "name": "generate_clicks",
    "target":{
      "type": "kafka",
      "endpoint": "kafka:9092",
      "topic": "clicks",
      "topic_key": ["user_id"]
      },
    "config_file": "clickstream/clickstream.json",
    "total_events":10000,
    "concurrency":100
}
```

### /jobs
Displays a list of currently running jobs, including their current status.
```
curl -X GET "http://localhost:9999/jobs"
```
```json
[ { "name": "gen_clickstream1", "config_file": "clickstream/clickstream.json", 
    "target": {"type": "file", "path": "/files/clicks1.json"}, 
    "active_sessions": 100, "total_records": 2405, "start_time": "2023-08-02 22:11:39", 
    "run_time": 462.520603, 
    "status": "RUNNING"}, 
  { "name": "gen_clickstream2", "config_file": "clickstream/clickstream.json", 
    "target": {"type": "file", "path": "/files/clicks2.json"}, 
    "active_sessions": 100, "total_records": 2383, "start_time": "2023-08-02 22:11:40", 
    "run_time": 461.291613, 
    "status": "RUNNING"}, 
  { "name": "gen_clickstream3", "config_file": "clickstream/clickstream.json", 
    "target": {"type": "file", "path": "/files/clicks3.json"}, 
    "active_sessions": 100, "total_records": 2428, "start_time": "2023-08-02 22:11:40", 
    "run_time": 461.533282, 
    "status": "RUNNING"}]
```

### /stop/\<job name>
This request will stop the job named <job_name> if it is running. 

It also removes the job from the list of known jobs as displayed in the /jobs API.

Example:
```
curl -X POST "http://localhost:9999/stop/gen_clickstream1"
```
```json
{"message":"Job [gen_clickstream1] stopped successfully."}
```

### /status/\<job_name>
Displays the definition and current status of the job named <job_name>.
Example:
```
curl "http://localhost:9999/status/gen_clickstream1"
```

```json
{ "name": "gen_clickstream1", "config_file": "clickstream/clickstream.json", 
    "target": {"type": "file", "path": "/files/clicks1.json"}, 
    "active_sessions": 100, "total_records": 2405, "start_time": "2023-08-02 22:11:39", 
    "run_time": 462.520603, 
    "status": "RUNNING"}
```

### /files
Displays the definition and current status of the job named <job_name>.
Example:
```
curl "http://localhost:9999/files"
```
```json
["sample_data.json", "clicks.json", "clicks1.json", "clicks2.json", "clickstream_data.json", "clicks3.json"]
```

### /file/<file_name>
Displays the definition and current status of the job named <job_name>.
Example:
```
curl "http://localhost:9999/file/clicks.json"  | tail -5
```
```json
{"time":"2023-08-02T22:27:48.418","user_id":"2142","event_type":"view_cart","client_ip":"127.250.32.144","client_device":"desktop","client_lang":"Arabic","client_country":"Indonesia","referrer":"bing.com/search","keyword":"gifts","product":"Electric shock pen"}
{"time":"2023-08-02T22:27:48.431","user_id":"2586","event_type":"view_product","client_ip":"127.174.137.91","client_device":"mobile","client_lang":"Mandarin","client_country":"Nigeria","referrer":"amazon.com","keyword":"t-shirts","product":"Toilet golf putting green"}
{"time":"2023-08-02T22:27:48.710","user_id":"3850","event_type":"search","client_ip":"127.167.21.193","client_device":"mobile","client_lang":"French","client_country":"Nigeria","referrer":"google.com/search","keyword":"Geeky gifts","product":"Novelty toilet paper"}
{"time":"2023-08-02T22:27:48.899","user_id":"3846","event_type":"view_product","client_ip":"127.74.91.52","client_device":"laptop","client_lang":"English","client_country":"China","referrer":"google.com/search","keyword":"Geeky gifts","product":"Rubber chicken"}
{"time":"2023-08-02T22:27:48.905","user_id":"1966","event_type":"search","client_ip":"127.167.136.121","client_device":"mobile","client_lang":"English","client_country":"United States","referrer":"bing.com/search","keyword":"Gag gifts","product":"Bubble wrap suit"}
```


## Command Line Execution 

The Druid Data Driver is a python script that simulates a workload that generates data for Druid ingestion.
You can use a JSON config file to describe the characteristics of the workload you want the Druid Data Driver to simulate.
The script uses this config file to generate JSON records.

Here are the commands to set up the Python environment:

```
apt-get install python3
apt-get update
apt-get install -y python3-pip

pip install confluent-kafka
pip install python-dateutil
pip install kafka-python
pip install numpy
pip install sortedcontainers
```

Run the program as follows:

```python generator/DruidDataDriver.py <options>```

Options include:

```
-f <configuration definition file name>
-o <target definition file name>
-s <start time in ISO format (optional)>
-n <total number of records to generate>
-t <duration for generating records>
```

Use the _-f_ option to designate a configuration file name.
If you omit the _-f_ option, the script reads the configuration from _stdin_.

Use the _-o_ option to designate a target definition file name. The [target](###"target"_object) defines where the generated messages are sent.

The _-s_ option tells the driver to use simulated time instead of wall clock time (the default).
The simulated clock starts at the time specified by the argument (or the current time if no argument is specified) and
advances the simulated clock based on the generated events (i.e., records).
When used with the _-t_ option, the simulated clock simulates the duration.
This option is useful for generating batch data as quickly as possible.

The other two options control how long the script runs.
If neither option is present, the script will run indefinitely.
The _-t_ and _-n_ options are exclusive (use one or the other).
Time durations may be specified in terms of seconds, minutes or hours.
For example, specify 30 seconds as follows:

```
-t 30S
```

Specify 10 minutes as follows:

```
-t 10M
```

Or, specify 1 hour as follows:

```
-t 1H
```

#### Example Command Line run:

Create a file for the target definition with:
```
echo '{"type":"stdout"}' > /tmp/target
```
Run with a predefined data generation config file for 10 seconds:
```
python3.11 generator/DruidDataDriver.py -f clickstream/clickstream.json -o /tmp/target -t 10s

{"__time":"2023-07-28T16:26:39.744","user_id":"2816","event_type":"login","client_ip":"127.157.215.28","client_device":"desktop","client_lang":"Spanish","client_country":"Vietnam","referrer":"bing.com/search","keyword":"None","product":"None"}
{"__time":"2023-07-28T16:26:39.886","user_id":"3273","event_type":"login","client_ip":"127.253.19.98","client_device":"mobile","client_lang":"Mandarin","client_country":"Indonesia","referrer":"adserve.com","keyword":"None","product":"None"}
{"__time":"2023-07-28T16:26:39.901","user_id":"1565","event_type":"home","client_ip":"127.220.178.38","client_device":"mobile","client_lang":"Russian","client_country":"Philippines","referrer":"bing.com/search","keyword":"None","product":"None"}
{"__time":"2023-07-28T16:26:39.936","user_id":"3875","event_type":"login","client_ip":"127.33.246.91","client_device":"mobile","client_lang":"French","client_country":"Bazil","referrer":"twitter.com/post","keyword":"None","product":"None"}
{"__time":"2023-07-28T16:26:40.204","user_id":"654","event_type":"login","client_ip":"127.33.184.203","client_device":"desktop","client_lang":"English","client_country":"United States","referrer":"amazon.com","keyword":"None","product":"None"}
```



## Data Generator Target
The target defines where the data will be written or published.

### "target" object

There are four flavors of targets: _stdout_, _file_, _kafka_, and _confluent_.

_stdout_ targets print the JSON records to standard out and have the form:

```
"target": {
  "type": "stdout"
}
```

_file_ targets write records to the specified file and have the following format:

```
"target": {
  "type": "file",
  "path": "<filename goes here>"
}
```

Where:
- <i>path</i> is the path and file name

_kafka_ targets write records to a Kafka topic and have this format:

```
"target": {
  "type": "kafka",
  "endpoint": "<ip address and optional port>",
  "topic": "<topic name>",
  "topic_key": [<list of key fields>],
  "security_protocol": "<protocol designation>",
  "compression_type": "<compression type designation>"
}
```

Where:
- <i>endpoint</i> is the IP address and optional port number (e.g., "127.0.0.1:9092") - if the port is omitted, 9092 is used
- <i>topic</i> is the topic name as a string
- <i>topic_key</i> (optional) is the list of generated fields used to build the key for each message
- <i>security_protocol</i> (optional) a protocol specifier ("PLAINTEXT" (default if omitted), "SSL", "SASL_PLAINTEXT", "SASL_SSL")
- <i>compression_type</i> (optional) a compression specifier ("gzip", "snappy", "lz4") - if omitted, no compression is used

_confluent_ targets write records to a Confluent topic and have this format:

```
"target": {
  "type": "confluent",
  "servers": "<bootstrap servers>",
  "topic": "<topic name>",
  "topic_key": [<list of key fields>],
  "username": "<username>",
  "password": "<password>"
}
```

Where:
- <i>servers</i> is the confluent servers (e.g., "pkc-lzvrd.us-west4.gcp.confluent.cloud:9092")
- <i>topic</i> is the topic name as a string
- <i>topic_key</i> (optional) is the list of generated fields used to build the key for each message
- <i>username</i> cluster API key
- <i>password</i> cluster API secret



## Data Generator Configuration

The config JSON object describes the characteristics of the workload you want to simulate (see the _examples_ folder for example config files).
A workload consists of a state machine, where each state outputs a record.
New state machines are instantiated based on the `interarrival` property.
Each state machine can be used to simulate the events generated by an entity like device (IoT) or a user session (clickstream).
Each state machine is probabilistic, which means that the state transitions may be stochastic based on probabilities.
Each state in the state machine performs four operations:
- First, the state sets any variable values
- Next, the state emits a record (based on an emitter description)
- The state delays for some period of time (based on a distribution)
- Finally, the state selects and transitions to a different state (based on a probabilistic transition table)

Emitters are record generators that output records as specified in the emitter description.
Each state employs a single emitter, but the same emitter may be used by many states.

The config JSON has the following format:

```
{
  "emitters": [...],
  "interarrival": {...},
  "states": [...]
}
```

The _emitters_ list is a list of record generators.
The _interarrival_ object describes the inter-arrival times (i.e., inverse of the arrival rate) of entities to the state machine
The _states_ list is a description of the state machine

### Distribution descriptor objects

Use _distribution descriptor objects_ to parameterize various characteristics of the config file (e.g., inter-arrival times, dimension values, etc.) according to the config file syntax described in this document.

There are four types of _distribution descriptor objects_: Constant, Uniform, Exponential and Normal. Here are the formats of each of these types:

#### Constant distributions

The constant distribution generates the same single value.

```
{
  "type": "constant",
  "value": <value>
}
```

Where _value_ is the value generated by this distribution.

#### Uniform distribution

Uniform distribution generates values uniformly between _min_ and _max_ (inclusive).

```
{
  "type": "uniform",
  "min": <value>,
  "max": <value>
}
```

Where:
- _min_ is the minimum value sampled
- _max_ is the maximum value sampled

#### Exponential distribution

Exponenital distributions generate values following an exponential distribution around the mean.

```
{
  "type": "exponential",
  "mean": <value>
}
```

Where _mean_ is the resulting average value of the distribution.

#### Normal distribution

Normal distributions generate values with a normal (i.e., bell-shaped) distribution.

```
{
  "type": "normal",
  "mean": <value>,
  "stddev": <value>
}

```

Where:
- _mean_ is the average value
- _stddev_ is the stadard deviation of the distribution

Note that negative values generated by the normal distribution may be forced to zero when necessary (e.g., interarrival times).


### "emitters": []

The _emitters_ list is a list of record generators.
Each emitter has a name and a list of dimensions, where the list of dimensions describes the records the emitter will generate.

An example of an emitter list looks as follows:

```
"emitters": [
  {
    "name": "short-record",
    "dimensions": [...]
  },
  {
    "name": "long-record",
    "dimensions": [...]
  }
]
```

#### "dimensions": []

The _dimensions_ list contains specifications for all dimensions (except the <i>__time</i> dimension, which is always the first dimension in the output record specified in UTC ISO 8601 format, and has the value of when the record is actually generated).

##### Cardinality

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

##### Dimension list item types

Dimension list entries include:

###### { "type": "enum" ...}

Enum dimensions specify the set of all possible dimension values, as well as a distribution for selecting from the set.
Enums have the following format:

```
{
  "type": "enum",
  "name": "<dimension name>",
  "values": [...],
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>values</i> is a list of the values
- <i>cardinality_distribution</i> informs the cardinality selection of the generated values
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)


###### { "type": "string" ...}

String dimension specification entries have the following format:

```
{
  "type": "string",
  "name": "<dimension name>",
  "length_distribution": <distribution descriptor object>,
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "chars": "<list characters used to build strings>",
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>length_distribution</i> describes the length of the string values - Some distribution configurations may result in zero-length strings
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> informs the cardinality selection of the generated values (omit if cardinality is zero)
- <i>chars</i> (optional) is a list (e.g., "ABC123") of characters that may be used to generate strings - if not specified, all printable characters will be used
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)

###### { "type": "counter" ...}

Counter dimensions are values that increment each time they occur in a record (counters are not incremented when they are missing or null).
Counters may be useful for dimensions simulating serial numbers, etc.
Counter dimension specification entries have the following format:

```
{
  "type": "counter",
  "name": "<dimension name>",
  "start": "<counter starting value (optional)>",
  "increment": "<counter increment value (optional)>",
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>start</i> is the initial value of the counter. (optional - the default is 0)
- <i>increment</i> is the amount to increment the value (optional - the default is 1)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)

##### { "type": "int" ...}

Integer dimension specification entries have the following format:

```
{
  "type": "int",
  "name": "<dimension name>",
  "distribution": <distribution descriptor object>,
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>distribution</i> describes the distribution of values the driver generates (rounded to the nearest int value)
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated values
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)

###### { "type": "float" ...}

Float dimension specification entries have the following format:

```
{
  "type": "float",
  "name": "<dimension name>",
  "distribution": <distribution descriptor object>,
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>,
  "precision": <number of digits after decimal>
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>distribution</i> describes the distribution of float values the driver generates
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated values
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)
- <i>precision</i> (optional) the number digits after the decimal - if omitted all digits are included

###### { "type": "timestamp" ...}

Timestamp dimension specification entries have the following format:

```
{
  "type": "timestamp",
  "name": "<dimension name>",
  "distribution": <distribution descriptor object>,
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>distribution</i> describes the distribution of timestamp values the driver generates
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated timestamps (optional - omit for unconstrained cardinality)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)


###### { "type": "ipaddress" ...}

IP address dimension specification entries have the following format:

```
{
  "type": "ipaddress",
  "name": "<dimension name>",
  "distribution": <distribution descriptor object>,
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>distribution</i> describes the distribution of IP address values the driver generates
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated IP addresses (optional - omit for unconstrained cardinality)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)


Note that the data driver generates IP address values as <i>int</i>s according to the distribution, and then converts the int value to an IP address.

###### { "type": "variable" ...}

Variables are values that may be set by states and have the following format:

```
{
  "type": "variable",
  "name": "<dimension name>"
  "variable": "<name of variable>"
}
```

Where:
- <i>name</i> is the name of the dimension
- <i>variable</i> is the name of variable with a previously set value

###### { "type": "object" ...}

Object dimensions create nested data. Object dimension specification entries have the following format:

```
{
  "type": "object",
  "name": "<dimension name>",
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>,
  "dimensions": [<list of dimensions nested within the object>]
}
```

Where:
- <i>name</i> is the name of the object
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated objects (optional - omit for unconstrained cardinality)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)
- <i>dimensions</i> is a list of nested dimensions

###### { "type": "list" ...}

list dimensions create lists of dimesions. List dimension specification entries have the following format:

```
{
  "type": "list",
  "name": "<dimension name>",
  "length_distribution": <distribution descriptor object>,
  "selection_distribution": <distribution descriptor object>,
  "elements": [<a list of dimension descriptions>],
  "cardinality": <int value>,
  "cardinality_distribution": <distribution descriptor object>,
  "percent_missing": <percentage value>,
  "percent_nulls": <percentage value>
}
```

Where:
- <i>name</i> is the name of the object
- <i>length_distribution</i> describes the length of the resulting list as a distribution
- <i>selection_distribution</i> informs the generator which elements to select for the list from the elements list
- <i>elements</i> is a list of possible dimensions the generator may use in the generated list
- <i>cardinality</i> indicates the number of unique values for this dimension (zero for unconstrained cardinality)
- <i>cardinality_distribution</i> skews the cardinality selection of the generated lists (optional - omit for unconstrained cardinality)
- <i>percent_missing</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for omitting this dimension from records (optional - the default value is 0.0 if omitted)
- <i>percent_nulls</i> a value in the range of 0.0 and 100.0 (inclusive) indicating the stochastic frequency for generating null values (optional - the default value is 0.0 if omitted)


List configuration can seem a bit confusing.
So to clarify, the generator will generate a list that is the length of a sample from the <i>length_distribution</i>.
The types of the elements of the list are selected from the <i>elements</i> list by using an index into the elements list that is determined by sampling from the <i>selection_distribution</i>.
The other field values (e.g., <i>cardinality</i>, <i>percent_nulls</i>, etc.) operate like the other types, but in this case apply to the entire list.


### "interarrival":{}

The _interarrival_ object is a _distribution descriptor object_ that describes the inter-arrival times (in seconds) between records that the driver generates.

One can calculate the mean inter-arrival time by dividing a period of time by the number of records to generate during the time period. For example, 100 records per hour has an inter-arrival time of 36 seconds per record (1 hour * 60 minutes/hour * 60 seconds/minute / 100 records).

See the previous section on _Distribution descriptor objects_ for the syntax.

### "states": []

The _states_ list is a list of state objects.
These state objects describe each of the states in a probabilistic state machine.
The first state in the list is the initial state in the state machine, or in other words, the state that the machine enters initially.

#### State objects

State objects have the following form:

```
{
  "name": <state name>,
  "emitter": <emitter name>,
  "variables": [...]
  "delay": <distribution descriptor object>,
  "transitions": [...]
}
```

Where:
- <i>name</i> is the name of the state
- <i>emitter</i> is the name of the emitter this state will use to generate a record
- <i>variables</i> (optional) a list of dimension objects where the dimension name is used as the variable name
- <i>delay</i> a distribution function indicating how long (in seconds) to remain in the state before transitioning
- <i>transitions</i> is a list of transition objects specifying possible transitions from this state to the next state


##### Transition Objects

Transition objects describe potential state transitions from the current state to the next state.
These objects have the following form:

```
{
  "next": <state name>,
  "probability": <probability value>
}
```

Where:

- <i>next</i> is the name of the next state
- <i>probability</i> is a value greater than zero and less than or equal to one.

Note that the sum of probabilities of all probabilities in the _transitions_ list must add up to one.
Use:

```
"next": "stop",
```

to transition to a terminal state.
