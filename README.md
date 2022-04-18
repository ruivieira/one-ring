# one-ring

> One Ring to *rule* them all

Three different approaches to execute rules.

## Approach 1: Durable rules proxying

## Approach 2: REST server wrapping

### Example

```python
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
```

## Approach 3: Drools bindings