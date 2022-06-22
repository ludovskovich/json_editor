import json


class JsonReader:

    def open_json_as_dict(self, path):
        file = open(path, "r")
        data = json.loads(file.read())
        for key in data:
            print(key, " = ", data[key])

        file.close()
        return data

    def save_json(self, path, object):
        if len(path) > 0:
            file = open(path, "w")
            data = json.dumps(object)
            file.write(data)

            file.close()

