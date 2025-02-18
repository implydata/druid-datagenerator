## Generate data over HTTP

Start the data generator by using the latest image from Imply:

```
docker run -d -p 9999:9999 imply/datagen:latest
```

### /list
Lists the data generator specifications available on the server.
Example:

```
curl "http://localhost:9999/list"
```

Output: 

```
["clickstream/clickstream.json","clickstream/users_changes.json"]
```

### /start
Initiates a data generation process with the specified specification. The specification can be selected from the available specifications by using the `config_file` property in the request. Alternatively, a custom specification can be provided in the `config` property.
The payload for this request has the following format:
```json
{
    "name": "<job name>",
    "target": "<target specification>",
    "config": "<generator specification JSON>",
    "config_file": "<name of the generator specification file on the server>",
    "total_events": "<total number of messages to generate>",
    "concurrency": "<max number of concurrent state machines>",
    "time": "<duration for data generation>",
    "time_type": "SIM | REAL | <start timestamp>"
}
```
Where:
- _"name"_ - (required) unique name for the job
- _"target"_ - (required) describes where to publish generated data.
- _"config"_ - (_config_ or _config_file_ required) custom generator specification JSON object.
- _"config_file"_ - (_config_ or _config_file_ required) [predefined specification](###GET_/list) is used.
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
Displays the list of files that have been created and are available for batch retrieval.
Example:
```
curl "http://localhost:9999/files"
```
```json
["sample_data.json", "clicks.json", "clicks1.json", "clicks2.json", "clickstream_data.json", "clicks3.json"]
```

### /file/<file_name>
Downloads the file named <file_name>.
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