import json

from ring import Ring
import logging

logging.basicConfig(level=logging.DEBUG)


def test_simple():
    with Ring("name") as rules:
        @rules.rule(name="R1", condition='subject == "World"')
        def my_function_a():
            logging.info("Hello World")

        @rules.rule(name="R2", condition='subject == "myself"')
        def my_function_b():
            logging.info("Hello to myself!")

        @rules.rule(
            name="R3", condition={"any": ['subject == "World"', 'subject == "myself"']}
        )
        def my_function_c():
            logging.info("Hello to myself and the World!")

        @rules.rule(
            name="R4", condition={"all": ['subject == "World"', 'subject == "myself"']}
        )
        def my_function_d():
            logging.info("Can't please everyone...")

        rules.create_rules_executor()

        result1 = rules.process({"subject": "World"})
        logging.debug(result1)
        assert len(result1) == 2
        assert result1[0]['ruleName'] == 'R1'
        assert result1[1]['ruleName'] == 'R3'

        result2 = rules.process({"subject": "myself"})
        logging.debug(result2)
        assert len(result2) == 2
        assert result2[0]['ruleName'] == 'R2'
        assert result2[1]['ruleName'] == 'R3'


def test_all():
    with Ring("name") as rules:
        @rules.all(name="R1", condition=['subject == "World"', 'name == "Rui"'])
        def my_function_a():
            logging.info("Hello World and Rui")

        rules.create_rules_executor()

        for value in ["World", "Moon", "Rui"]:
            result = rules.process({"subject": value})
            logging.debug(result)
            assert len(result) == 0

        result = rules.process({"subject": "Moon",  "name": "Rui"})
        logging.debug(result)
        assert len(result) == 0

        result = rules.process([{"subject": "World"},  {"name": "Rui"}])
        logging.debug(result)
        print(result)
        assert len(result) == 1

def test_any():
    with Ring("name") as rules:
        @rules.any(name="R1", condition=['flavour == "Vanilla"', 'topping == "Strawberry"'])
        def my_function_a():
            logging.info("Vanilla or strawberry")

        rules.create_rules_executor()

        for value in ["Chocolate", "Coconut", "Mint"]:
            result = rules.process({"flavour": value})
            logging.debug(result)
            assert len(result) == 0

        result = rules.process([{"flavour": "Mint"},  {"flavour": "Vanilla"}])
        logging.debug(result)
        assert len(result) == 1

        result = rules.process([{"topping": "Strawberry"},  {"flavour": "Coconut"}])
        logging.debug(result)
        print(result)
        assert len(result) == 1

        result = rules.process([{"topping": "Chocolate"},  {"flavour": "Coffee"}])
        logging.debug(result)
        print(result)
        assert len(result) == 0

def test_multiple():
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