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
