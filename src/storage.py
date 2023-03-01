import os
import pickle
import zlib
from github import Github


class Storage:
    "Object storage (base class)"

    def __init__(self):
        self.folder = "data"

    def get(self, name):
        "Get one object from the folder"
        data = self._get(name)
        return self.deserialize(data)

    def put(self, name, obj):
        "Put the object into the folder"
        data = self.serialize(obj)
        self._put(name, data)
        return data

    def list(self):
        "List object names from the folder"
        all_files = self._list()
        if "questions.csv" in all_files:
            all_files.remove("questions.csv")
        return all_files

    def delete(self, name):
        "Delete the object from the folder"
        self._delete(name)

    # IMPLEMENTED IN SUBCLASSES
    def _put(self, name, data):
        ...

    def _get(self, name):
        ...

    def _delete(self, name):
        pass

    # # #

    def serialize(self, obj):
        raw = pickle.dumps(obj)
        compressed = self.compress(raw)
        return compressed

    def deserialize(self, compressed):
        raw = self.decompress(compressed)
        obj = pickle.loads(raw)
        return obj

    def compress(self, data):
        return zlib.compress(data)

    def decompress(self, data):
        return zlib.decompress(data)


class DictStorage(Storage):
    "Dictionary based storage"

    def __init__(self, data_dict):
        super().__init__()
        self.data = data_dict

    def _put(self, name, data):
        if self.folder not in self.data:
            self.data[self.folder] = {}
        self.data[self.folder][name] = data

    def _get(self, name):
        return self.data[self.folder][name]


class LocalStorage(Storage):
    "Local filesystem based storage"

    def __init__(self, path):
        if not path:
            raise Exception("No storage path in environment variables!")
        super().__init__()
        self.path = os.path.join(path, self.folder)
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def _put(self, name, data):
        with open(os.path.join(self.path, name), "wb") as f:
            f.write(data)

    def _get(self, name):
        with open(os.path.join(self.path, name), "rb") as f:
            data = f.read()
        return data

    def _list(self):
        return os.listdir(self.path)

    def _delete(self, name):
        os.remove(os.path.join(self.path, name))


class GitHubStorage(Storage):
    "GitHub repository based storage"

    def __init__(self, access_token, owner_name, repo_name):
        if (not repo_name) or (not access_token):
            raise Exception("No GitHub credentials in environmental variables!")
        super().__init__()
        self.access_token = access_token
        self.owner_name = owner_name
        self.repo_name = repo_name
        self.repo = None
        self._authenticate()

    def _authenticate(self):
        g = Github(self.access_token)
        self.repo = g.get_user(self.owner_name).get_repo(self.repo_name)

    def _put(self, name, data):
        path = os.path.join(self.folder, name)
        try:
            contents = self.repo.get_contents(path)
            self.repo.update_file(contents.path, "Updated " + name, data, contents.sha)
        except Exception:
            self.repo.create_file(path, "Created " + name, data)

    def _get(self, name):
        path = os.path.join(self.folder, name)
        contents = self.repo.get_contents(path)
        # return contents.decoded_content
        return contents.raw_data
        return contents.decoded_content.decode("utf-8")

    def _list(self):
        contents = self.repo.get_contents(self.folder)
        return [c.name for c in contents]

    def _delete(self, name):
        path = os.path.join(self.folder, name)
        self.repo.delete


def get_storage(data_dict):
    "get storage adapter configured in environment variables"

    mode = os.getenv("STORAGE_MODE", "").upper()
    path = os.getenv("STORAGE_PATH", "")

    repo_name = os.getenv("GITHUB_REPO_NAME", "")
    onwer_name = os.getenv("GITHUB_OWNER_NAME", "")
    access_token = os.getenv("GITHUB_ACCESS_TOKEN", "")

    if mode == "GITHUB":
        storage = GitHubStorage(access_token, onwer_name, repo_name)
    elif mode == "LOCAL":
        storage = LocalStorage(path)
    else:
        storage = DictStorage(data_dict)
    return storage
