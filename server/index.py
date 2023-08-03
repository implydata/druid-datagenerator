from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime, timedelta
import dateutil.parser
import os, errno
import json
import threading


from generator import DruidDataDriver

class DataGeneratorServer (threading.Thread):
    def __init__(self, job_definition:dict):
        super(DataGeneratorServer, self).__init__()
        self._stop = threading.Event()
        self.config = None

        if 'name' in job_definition.keys():
            self.name = job_definition['name']
        else:
            raise KeyError('Job "name" property must be specified.')

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
                self.start_time = self.start_time + timedelta(seconds=0.001)
                self.time_type = 'SIM'
        else:
            self.time_type = None
            self.start_time = datetime.now()

        if (self.runtime is not None) and (self.total_recs is not None):
            raise ValueError("Use either 'time' or 'total_events', but not both.")


    def run(self):
        self.driver = DruidDataDriver.DataDriver(self.name, self.config, self.target, self.runtime, self.total_recs, self.time_type, self.start_time, self.max_entities)
        self.driver.simulate( )

    def report(self):
        return self.driver.report()

    def kill(self):
        self.driver.terminate()

    def get_name(self):
        return self.name




# flask application definition
app = Flask(__name__)

# save thread list so we can interact with it
server_list = []


def find_job(name):
    result = None
    for server in server_list:
        if server.get_name()==name:
            result=server
            break;
    return result

def delete_file(filename):
    try:
        if os.path.exists(filename):
            os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT: # already deleted
            raise # re-raise exception if a different error occurred

# REST ENDPOINTS

@app.route('/file/<path:path>')
def serve_file(path):
    try:
        return send_from_directory('/files', path, mimetype="Content-Type: text/html; charset=utf-16")
    except Exception as ex:
        return '{"message":"ERROR retrieving file ['+path+'].","exception":"'+f'{ex}'+'"}', 400


@app.route("/")
def instructions():
    return '{"message": "Data Generator server. POST to /start to initiate an data generator."}'

@app.route("/files")
def list_generated_files():
    try:
        rootDir='/files'
        files = [os.path.relpath(os.path.join(dirpath, file), rootDir) for (dirpath, dirnames, filenames) in os.walk(rootDir) for file in filenames]
        file_list = json.dumps(files)
        return file_list, 200
    except Exception as ex:
        return '{"message":"ERROR while listing available files.","exception":'+f'{ex}'+'}', 400

@app.route("/start", methods=['POST'])
def start_generator():
    try:
        job = request.get_json()
    except Exception as ex:
        raise ValueError(f"Failed to parse job payload, request: {request}\n {ex}")
    try:
        # place all generated files in the target path
        if 'name' not in job.keys():
            return '{"message":"ERROR job must have a "name" property."}', 400

        # check if job is already running
        existing_job = find_job(job['name'])
        if  existing_job is not None:
            if existing_job.report()['status'] == 'COMPLETE': # if job is complete then re-start it
                # remove existing job and continue
                existing_job.kill()
                server_list.remove(existing_job)
            else:
                return '{"message":"A Job with name ['+job['name']+'] is already running. Use /stop/'+job['name']+' to cancel it and try again."}', 400

        # only use the name of the file, strip any path, the files are generated and read from /files only
        if job['target']['type']=='file':
            filename = os.path.join('/files', os.path.basename(job['target']['path']))
            job['target']['path']=filename
            # since we are rebuilding the file remove it if it exists:
            delete_file(filename)
        server = DataGeneratorServer(job)
        server.start()
        server_list.append(server)
        job_result = json.dumps(job, indent=2)
        return '{"message":"Starting generator for request.", "request":'+job_result+'}', 200
    except Exception as ex:
        return '{"message":"ERROR starting data generator job","exception":"'+f'{ex}'+'"}', 400

@app.route("/jobs", methods=['GET'])
def get_jobs():
    result = []
    try:
        if len(server_list) == 0:
            return '{"message":"Data generation is NOT running."}', 200
        for server in server_list:
            report = server.report()
            result.append( report)
        return json.dumps(result), 200
    except Exception as ex:
        return '{"message":"ERROR in creating report.","exception":'+f'{ex}'+'}', 400

@app.route("/status/<name>", methods=['GET'])
def get_status(name):
    found=False
    try:
        if len(server_list) == 0:
            return '{"message":"Data generation is NOT running."}', 200
        for server in server_list:
            result = server.report()
            if result['name']==name:
                found=True
                break;
        if found:
            return json.dumps(result), 200
        else:
            return '{"message":"Job ['+name+'] not found"}', 400
    except Exception as ex:
        return '{"message":"ERROR in creating report.","exception":'+f'{ex}'+'}', 400


@app.route("/stop/<name>", methods=['POST'])
def stop_generator(name):
    try:
        server = find_job(name)
        if server is not None:
            server.kill()
            server_list.remove(server)
            return '{"message":"Job ['+name+'] stopped successfully."}', 200
        else:
            return '{"message":"Job ['+name+'] not found."}', 400
    except Exception as ex:
        return '{"message":"ERROR stopping job ['+name+'].","exception":'+f'{ex}'+'}', 400


@app.route("/list", methods=['GET'])
def list_configs():
    try:
        rootDir='./config_file'
        files = [os.path.relpath(os.path.join(dirpath, file), rootDir) for (dirpath, dirnames, filenames) in os.walk(rootDir) for file in filenames]
        config_list = json.dumps(files)
        return config_list, 200
    except Exception as ex:
        return '{"message":"ERROR while listing available configurations.","exception":'+f'{ex}'+'}', 400


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9999))
    app.run(debug=True, host='0.0.0.0', port=port)
