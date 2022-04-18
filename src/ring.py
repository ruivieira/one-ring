import json
from typing import Optional

import requests


class Ring:
    def __init__(self, name: str, host="0.0.0.0", port="8080"):
        self._name = name
        self._host = host
        self._port = port
        self._post_headers = {"Accept": "application/json", "Content-Type": "application/json"}
        self._BASE_URL = f"http://{self._host}:{self._port}"
        self._CREATE_RULES_EXECUTOR_URL = f"{self._BASE_URL}/create-rules-executor"
        self._rules = []
        self._references = {}
        self._id = None

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def _rules_executor_url(self, id: int) -> str:
        return f"{self._BASE_URL}/rules-executors/{id}/process"

    def add_rule(self, name, condition):
        self._rules.append({"name": name, "condition": condition})

    def add_reference(self, name, func):
        self._references[name] = func

    def create_rules_executor(self) -> Optional[int]:
        response = requests.post(self._CREATE_RULES_EXECUTOR_URL, data=json.dumps({'host_rules': self._rules}),
                                 headers=self._post_headers)
        print(response.request.body)
        if response.ok:
            _id = int(response.text)
            self._id = _id
            return _id
        else:
            return None

    def process(self, data):
        response = requests.post(self._rules_executor_url(self._id), data=json.dumps(data),
                                 headers=self._post_headers)

        result = json.loads(response.content)
        if len(result) > 0:
            for _rule in result:
                self._references[_rule['ruleName']].__call__()
        return result


def rule(ruleset, name, condition):
    def inner_decorator(f):
        def wrapped(*args, **kwargs):
            print('before function')
            response = f(*args, **kwargs)
            print('after function')
            return response

        ruleset.add_rule(name, condition)
        ruleset.add_reference(name, f)
        print(f"decorating {f} with argument ruleset={ruleset} and rule={condition}")
        return wrapped

    return inner_decorator


with Ring("name") as rule_set:
    @rule(ruleset=rule_set, name="R1", condition='subject == "World"')
    def my_function_a():
        print('Hello World')

    @rule(ruleset=rule_set, name="R2", condition='subject == "myself"')
    def my_function_b():
        print('Hello to myself!')

    @rule(ruleset=rule_set, name="R3", condition={"any": ['subject == "World"', 'subject == "myself"']})
    def my_function_c():
        print('Hello to myself and the World!')

    @rule(ruleset=rule_set, name="R4", condition={"all": ['subject == "World"', 'subject == "myself"']})
    def my_function_c():
        print("Can't please everyone...")

    rule_set.create_rules_executor()
    print(rule_set.process({"subject" : "World"}))
    print(rule_set.process({"subject": "myself"}))


