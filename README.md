# one-ring

> One Ring to *rule* them all

## Setup

All the examples in this repo require the rules REST server running.
The specific instructions on how to do this are available [here](https://github.com/mariofusco/drools-yaml-rules).

Install the Python dependencies with:

```shell
pip install -r requirements.txt
```

From the root of the project run

```shell
python -m pytest
```

## Example

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

### Syntactic sugar

The `@all` annotation applies to all logic:

```python
@rules.all(name="R1", condition=['subject == "World"', 'name == "Rui"'])
def my_function_a():
    # do something
```

Similarly the `@any` annotation adds the _any_ operator.

```python
@rules.any(name="R1", condition=['subject == "World"', 'name == "Rui"'])
def my_function_a():
    # do something
```

### Shenanigans

Using rules to choose the rules processor

```python
    rules1 = Ring("rules1")
    rules2 = Ring("rules2")
    rules3 = Ring("rules3")

    processor = None

    @rules1.rule(name="R1", condition='processor == 1')
    def my_function_a():
        nonlocal processor
        processor = rules1
    @rules1.rule(name="R2", condition='processor == 2')
    def my_function_b():
        nonlocal processor
        processor = rules2
    @rules1.rule(name="R3", condition='processor == 3')
    def my_function_c():
        nonlocal processor
        processor = rules3

    rules1.create_rules_executor()
    rules1.process({"processor": 3})

    @processor.rule(name="R1", condition='name == "me"')
    def my_function_d():
        print("Hello me!")

    processor.create_rules_executor()
    processor.process({"name": "me"})
```