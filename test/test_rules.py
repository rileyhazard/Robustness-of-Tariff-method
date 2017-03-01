from rule import Rule


def test_no_docstring_info():
    def fn():
        """
        Lorem ipsum
        """
        return True

    Rule(fn)


def test_no_docstring():
    def fn():
        return True
    rule_ = Rule(fn)
    assert rule_


def test_callable():
    def fn():
        return True

    rule_ = Rule(fn)
    assert rule_()


class TestParseModule(object):
    def test_parse_module(self):
        def fn():
            """
            Module: Adult
            """
            return True

        rule_ = Rule(fn)
        assert rule_.module == 'adult'

    def test_parse_module_with_trailing_string(self):
        def fn():
            """
            Module: Adult
            Lorem ipsum
            """
            return True

        rule_ = Rule(fn)
        assert rule_.module == 'adult'

    def test_parse_module_with_preceding_string(self):
        def fn():
            """
            Lorem ipsum
            Module: Adult
            """
            return True

        rule_ = Rule(fn)
        assert rule_.module == 'adult'

    def test_parse_module_sandwiched(self):
        def fn():
            """
            Lorem ipsum
            Module: Adult
            Lorem ipsum
            """
            return True

        rule_ = Rule(fn)
        assert rule_.module == 'adult'


class TestParsePrediciton(object):
    def test_parse_prediction(self):
        def fn():
            """
            Prediction: Cause
            """
            return True

        rule_ = Rule(fn)
        assert rule_.prediction == 'Cause'

    def test_parse_multiword_prediction(self):
        def fn():
            """
            Prediction: Some Multiword Cause
            """
            return True

        rule_ = Rule(fn)
        assert rule_.prediction == 'Some Multiword Cause'

    def test_parse_parse_predicition_sandwiched(self):
        def fn():
            """
            Lorem ipsum
            Prediction: Cause
            Lorem ipsum
            """
            return True

        rule_ = Rule(fn)
        assert rule_.prediction == 'Cause'


class TestParseQuestions(object):
    def test_parse_questions(self):
        def fn():
            """
            Lorem ipsum
            """
            q1 = row.get('A')
            q2 = row.get('B')
            q3 = row.get('C')
            return True

        rule_ = Rule(fn)
        assert rule_.questions == {'q1': 'A', 'q2': 'B', 'q3': 'C'}

    def test_parse_questions_with_defaults(self):
        def fn():
            """
            Lorem ipsum
            """
            q1 = row.get('A', 'foo')
            q2 = row.get('B', 0)
            q3 = row.get('C')
            return True

        rule_ = Rule(fn)
        assert rule_.questions == {'q1': 'A', 'q2': 'B', 'q3': 'C'}
