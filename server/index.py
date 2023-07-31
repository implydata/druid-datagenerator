from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import dateutil.parser
import os
import json
import threading


from generator import DruidDataDriver

class DataGeneratorServer (threading.Thread):
    def __init__(self, job_definition:dict):
        super(DataGeneratorServer, self).__init__()
        self._stop = threading.Event()
        self.config = None

        if 'config' in job_definition.keys():
            self.config = job_definition['config']
            self.config['config_file']='__custom__'

        if 'config_file' in job_definition.keys():
            with open(f"config_file/{job_definition['config_file']}", 'r') as f:
                self.config = json.load(f)
            self.config['config_file']=job_definition['config_file']

        # config is required
        if self.config is None:
            raise KeyError('A data generation "config" or "config_file" must be specified.')

        # target is required
        if not 'target' in job_definition.keys():
            raise KeyError('A data generation "target" must be specified')

        self.target = job_definition['target']

        if 'time' in job_definition.keys():
            self.runtime = job_definition['time']
        else:
            self.runtime = None

        if 'concurrency' in job_definition.keys():
            self.max_entities = job_definition['concurrency']
        else:
            self.max_entities = None

        if 'total_events' in job_definition.keys():
            self.total_recs = job_definition['total_events']
        else:
            self.total_recs = None

        if 'time_type' in job_definition.keys():
            self.time_type = job_definition['time_type']
            if self.time_type == 'SIM':
                self.start_time = datetime.now()
            elif self.time_type == 'REAL':
                self.start_time = datetime.now()
            else:
                self.start_time = dateutil.parser.isoparse(self.time_type)
                self.time_type = 'SIM'
        else:
            self.time_type = None
            self.start_time = datetime.now()

        if (self.runtime is not None) and (self.total_recs is not None):
            raise ValueError("Use either 'time' or 'total_events', but not both.")


    def run(self):
        self.driver = DruidDataDriver.DataDriver(self.config, self.target, self.runtime, self.total_recs, self.time_type, self.start_time, self.max_entities)
        self.driver.simulate( )

    def report(self):
        return self.driver.report()

    def kill(self):
        self.driver.terminate()




# flask application definition
app = Flask(__name__)
# save thread list so we can interact with it
server_list = []

# REST ENDPOINTS
@app.route("/")
def instructions():
    return "I am a data generator.\n POST to /start to initiate an data generator."

@app.route("/start", methods=['POST'])
def start_generator():
    try:
        job = request.get_json()
        job_result = json.dumps(job, indent=2)
    except Exception as ex:
        raise ValueError(f"Failed to parse job payload, request: {request}\n {ex}")
    try:
        server = DataGeneratorServer(job)
        server.start()
        server_list.append(server)
        return f"Starting generator for request [{job_result}]", 200
    except Exception as ex:
        return f'{ex}', 400

@app.route("/status")
def get_status():
    result = ''
    try:
        if len(server_list) == 0:
            return "No data generation running.", 200

        for server in server_list:
            report = server.report()
            result += '\n'+json.dumps(report)
        return result, 200
    except Exception as ex:
        return f'Error getting report: {ex}', 400

@app.route("/stop", methods=['POST'])
def stop_generator():
    try:
        for server in server_list:
            server.kill()
        server_list.clear()
        return "Data generation stopped", 200
    except Exception as ex:
        return f'{ex}', 400

@app.route("/list", methods=['GET'])
def list_configs():
    try:
        rootDir='./config_file'
        files = [os.path.relpath(os.path.join(dirpath, file), rootDir) for (dirpath, dirnames, filenames) in os.walk(rootDir) for file in filenames]
        config_list = json.dumps(files)
        return config_list, 200
    except Exception as ex:
        return f'{ex}', 400


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
