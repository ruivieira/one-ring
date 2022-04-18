# one-ring

> One Ring to *rule* them all

Three different approaches to execute rules.

## Approach 1: Durable rules proxying

## Approach 2: REST server wrapping

### Example

```python
with Ring("name") as rule_set:
    @rule(ruleset=rule_set, name="R1", condition='subject == "World"')
    def my_function():
        print('Hello World')

    @rule(ruleset=rule_set, name="R2", condition='subject == "myself"')
    def my_function():
        print('Hello to myself!')

    rule_set.create_rules_executor()
    print(rule_set.process({"subject" : "World"}))
    print(rule_set.process({"subject": "myself"}))
```

## Approach 3: Drools bindings