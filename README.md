# one-ring

> One Ring to *rule* them all

Three different approaches to execute rules.

## Approach 1: Durable rules proxying

## Approach 2: REST server wrapping

### Example

```python
with Ring("name") as rules:

    @rules.rule(name="R1", condition='subject == "World"')
    def my_function_a():
        print("Hello World")

    @rules.rule(name="R2", condition='subject == "myself"')
    def my_function_b():
        print("Hello to myself!")

    @rules.rule(name="R3", condition={"any": ['subject == "World"', 'subject == "myself"']})
    def my_function_c():
        print("Hello to myself and the World!")

    @rules.rule(name="R4", condition={"all": ['subject == "World"', 'subject == "myself"']})
    def my_function_d():
        print("Can't please everyone...")

    rules.create_rules_executor()
    print(rules.process({"subject": "World"}))
    print(rules.process({"subject": "myself"}))
```

## Approach 3: Drools bindings