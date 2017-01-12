from rule import Rule


def test_no_docstring_info():
    def fn():
        """
        Lorem ipsum
        """
        return True

    Rule(fn)


class TestParseModule(object):
    def test_parse_module(self):
        def fn():
            """
            Module: Adult
            """
            return True

        rule_ = Rule(fn)
        assert rule_.module == 'adult'

    def test_parse_two_modules(self):
        def fn():
            """
            Module: Adult and Child
            """
            return True

        rule_ = Rule(fn)
        assert rule_.module == ['adult', 'child']

    def test_parse_three_modules(self):
        def fn():
            """
            Module: Adult and Child and Neonate
            """
            return True

        rule_ = Rule(fn)
        assert rule_.module == ['adult', 'child', 'neonate']

    def test_parse_modules_different_order(self):
        def fn():
            """
            Module: Child and Adult
            """
            return True

        rule_ = Rule(fn)
        assert rule_.module == ['child', 'adult']

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

    def test_parse_two_predictions(self):
        def fn():
            """
            Prediction: Adult Cause (Child Cause)
            """
            return True

        rule_ = Rule(fn)
        assert rule_.prediction == ['Adult Cause', 'Child Cause']

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
            Questions:
                q1: A
                q2: B
                q3: C
            """
            return True

        rule_ = Rule(fn)
        assert rule_.questions == {'q1': 'A', 'q2': 'B', 'q3': 'C'}

    def test_parse_two_question_sets(self):
        def fn():
            """
            Module: Foo and Bar
            Foo questions:
                q1: A
                q2: B

            Bar questions:
                q1: C
                q2: D
            """
            return True

        rule_ = Rule(fn)
        assert rule_.questions == [{'q1': 'A', 'q2': 'B'},
                                   {'q1': 'C', 'q2': 'D'}]
