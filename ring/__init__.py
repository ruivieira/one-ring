import json
from typing import Dict, List, Optional
import logging
import requests

logging.basicConfig(level=logging.DEBUG)


class Proxy:
    def __init__(self, host="0.0.0.0", port="8080"):
        self._host = host
        self._port = port
        self._post_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self._BASE_URL = f"http://{self._host}:{self._port}"
        self._CREATE_RULES_EXECUTOR_URL = f"{self._BASE_URL}/create-rules-executor"
        self._id: Optional[int] = None

    @property
    def id(self):
        return self._id

    def _rules_executor_url(self, id: int) -> str:
        return f"{self._BASE_URL}/rules-executors/{id}/process"

    def create_rules_executor(self, rules: Dict) -> Optional[int]:
        response = requests.post(
            self._CREATE_RULES_EXECUTOR_URL,
            data=json.dumps(rules),
            headers=self._post_headers,
        )
        print(response.request.body)
        if response.ok:
            _id = int(response.text)
            self._id = _id
            logging.debug("Created executor with id=%i", _id)
            return _id
        else:
            return None

    def process(self, data: Dict) -> Dict:
        if len(data) == 1:
            data = [data]
        response = requests.post(
            self._rules_executor_url(self._id),
            data=json.dumps({"facts": data}),
            headers=self._post_headers,
        )
        return json.loads(response.content)


class Ring:
    def __init__(self, name: str, proxy=None):
        self._name = name
        if proxy:
            self._proxy = proxy
        else:
            self._proxy = Proxy()

        self._rules: List[Dict] = []
        self._references: Dict = {}

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def add_rule(self, name, condition):
        self._rules.append({"name": name, "condition": condition})

    @property
    def rules(self):
        return {"host_rules": self._rules}

    def add_reference(self, name, func):
        self._references[name] = func

    def create_rules_executor(self):
        self._proxy.create_rules_executor(self.rules)

    def process(self, data: Dict) -> Dict:
        if self._proxy.id:
            result = self._proxy.process(data)
            if len(result) > 0:
                for _rule in result:
                    name = _rule["ruleName"]
                    if name in self._references:
                        _func = self._references[name]
                        if _func.__code__.co_argcount > 0:
                            _func.__call__(result)
                        else:
                            _func.__call__()
            return result
        else:
            raise Exception("There is no associated ruleset id.")

    def rule(self, name, condition):
        def inner_decorator(f):
            def wrapped(*args, **kwargs):
                response = f(*args, **kwargs)
                return response

            self.add_rule(name, condition)
            self.add_reference(name, f)
            logging.debug(
                "decorating %s with argument ruleset=%s and rule=%s",
                f, self, condition
            )
            return wrapped

        return inner_decorator

    def all(self, name, condition):
        def inner_decorator(f):
            def wrapped(*args, **kwargs):
                response = f(*args, **kwargs)
                return response

            self.add_rule(name, {"all": condition})
            self.add_reference(name, f)
            logging.debug(
                "decorating %s with argument ruleset=%s and rule=%s",
                f, self, condition
            )
            return wrapped

        return inner_decorator

    def any(self, name, condition):
        def inner_decorator(f):
            def wrapped(*args, **kwargs):
                response = f(*args, **kwargs)
                return response

            self.add_rule(name, {"any": condition})
            self.add_reference(name, f)
            logging.debug(
                "decorating %s with argument ruleset=%s and rule=%s",
                f, self, condition
            )
            return wrapped

        return inner_decorator

    @staticmethod
    def fromJSON(name: str, data):
        ring = Ring(name)
        for rule in data['host_rules']:
            ring.add_rule(rule['name'], rule['condition'])
        return ring
