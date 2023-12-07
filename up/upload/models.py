import os
import json
import base64
import hashlib
from datetime import date
import time
import re
import copy

class Upload:
    JSMode = 1  # 1 -> old ; 2 -> modern
    JSObject = "Upload"
    JSCall = "newUpload"
    rootDir = None
    inputs = {}
    profiles = {}

    @staticmethod
    def addProfile(name, config):
        if 'folder' in config:
            last = config['folder'][-1]
            if last == '/' or last == "\\":
                config['folder'] = config['folder'][:-1]
        Upload.profiles[name] = {
            "config": config,
            "key": hashlib.md5(name.encode()).hexdigest(),
            "name": name
        }

    @staticmethod
    def getProfile(profile):
        if profile in Upload.profiles:
            return Upload.profiles[profile]
        md5 = hashlib.md5(profile.encode()).hexdigest()
        if md5 in Upload.profiles:
            return Upload.profiles[md5]
        return False

    @staticmethod
    def addInput(input_name, profile):
        if profile not in Upload.inputs:
            Upload.inputs[profile] = []
        if input_name not in Upload.inputs[profile]:
            Upload.inputs[profile].append(input_name)

    @staticmethod
    def addVar(var_key, var_value, profile):
        Upload.profiles[profile]['vars'] = [{var_key: var_value}]

    @staticmethod
    def setRootDir(directory):
        Upload.rootDir = directory

    @staticmethod
    def setProfiles(profile="all"):
        # Crie uma cópia profunda dos dados originais sem modificar o original
        copied_profiles = copy.deepcopy(Upload.profiles)

        for profile_name, profile_data in copied_profiles.items():
            profile_data['config'].pop('folder', None)

        if profile != "all" and profile not in copied_profiles:
            return False

        if profile == "all":
            for upload_profile, inputs in Upload.inputs.items():
                if upload_profile in copied_profiles:
                    copied_profiles[upload_profile]['inputNames'] = inputs
        else:
            copied_profiles[profile]['inputNames'] = Upload.inputs[profile]

        return copied_profiles if profile == "all" else copied_profiles[profile]

    @staticmethod
    def saveFile(file_name, data, folder):
        if not os.path.isdir(folder):
            os.makedirs(folder, 0o775, True)
            os.chmod(folder, 0o775)

        file_id = hashlib.md5(file_name.encode()).hexdigest()
        json_data = {
            "name": file_name,
            "date": date.today().strftime("%Y-%m-%d"),
            "status": "uploading"
        }

        log_file = os.path.join(folder, "upload.log.json")

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log = json.load(f)
                log[file_id] = json_data
        else:
            log = {file_id: json_data}

        with open(log_file, 'w') as f:
            json.dump(log, f)

        Upload.removeTrash(folder)

        file_path = os.path.join(folder, file_name)
        with open(file_path, 'ab') as f:
            data = data.split(',')
            f.write(base64.b64decode(data[1].replace(" ", "+")))

        return True

    @staticmethod
    def removeTrash(folder):
        log_file = os.path.join(folder, "upload.log.json")

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log = json.load(f)
                current_date = date.today().strftime("%Y-%m-%d")

                for file_id, data in log.items():
                    if data["date"] != current_date:
                        file_path = os.path.join(folder, data["name"])
                        os.unlink(file_path)
                        del log[file_id]

            with open(log_file, 'w') as f:
                json.dump(log, f)

        return True

    @staticmethod
    def unsetLog(file_name, folder):
        log_file = os.path.join(folder, "upload.log.json")

        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log = json.load(f)
                file_id = hashlib.md5(file_name.encode()).hexdigest()
                if file_id in log:
                    del log[file_id]

                    if not log:
                        os.unlink(log_file)
                    else:
                        with open(log_file, 'w') as f:
                            json.dump(log, f)

                    return True

        return False

    @staticmethod
    def delete(file_path):
        if os.path.exists(file_path) and not bool(re.search(r'\.(php|js|css|html)$', file_path)):
            try:
                os.unlink(file_path)
                return True
            except Exception:
                return False
        return False

    @staticmethod
    def setNewName(source):
        aux = source.split(".")
        extension = aux[-1]
        aux = ".".join(aux[:-1])
        new_name = re.sub(r'[^a-zA-Z0-9.]', '-', aux) + hashlib.md5(source.encode()).hexdigest() + hashlib.md5(str(time.time()).encode()).hexdigest() + '.' + extension
        return new_name

    @staticmethod
    def init(profile="all"):
        return Upload.setProfiles(profile)
        


