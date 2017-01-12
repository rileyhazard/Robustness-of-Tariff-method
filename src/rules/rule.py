from collections import OrderedDict
import itertools
import re


class Rule(object):
    """Wrapper class for rule functions

    """

    def __init__(self, func, name=None, module=None, prediction=None,
                 questions=None, conditions=None, notes=None, footnotes=None,
                 cases=None):
        self.func = func
        self.name = name if name else func.__name__
        self.module = module if module else self.parse_module()
        self.prediction = prediction if prediction else self.parse_prediction()
        self.questions = questions if questions else self.parse_questions()
        self.conditions = conditions if conditions else self.parse_conditions()
        self.notes = notes if notes else self.parse_notes()
        self.footnotes = footnotes if footnotes else self.parse_footnotes()
        self.cases = cases if cases else self.parse_cases()

    def parse_module(self):
        """Parse the module from the rule function docstring"""
        modules = re.findall('(?<=Module: ).+?(?=\n)', self.func.__doc__)
        if modules:
            modules = map(str.lower, modules[0].split(' and '))
        if len(modules) == 1:
            return modules[0]
        return modules

    def parse_prediction(self):
        """Parse the prediction from the rule function docstring"""
        pred = re.findall('(?<=Prediction: ).+?(?=\n)', self.func.__doc__)
        if pred:
            pred = pred[0]
        if '(' in pred:
            pred = re.findall('^.+?(?= \()|(?<=\().*(?=\))', pred)
        return pred

    def parse_questions(self):
        """Parse the list of questions from the rule function docstring"""
        if isinstance(self.module, basestring) or not self.module:
            questions = self._parse_multiline('(?<=Questions:\n).*')
            return OrderedDict([q.split(': ') for q in questions])
        else:
            tmp = '(?<={} questions:\n).*'
            questions = [self._parse_multiline(tmp.format(module.title()))
                         for module in self.module]
            return [OrderedDict([q.split(': ') for q in qs])
                    for qs in questions]

    def _parse_multiline(self, pattern):
        lines = re.findall(pattern, self.func.__doc__, re.S)
        if not lines:
            return ''
        lines = map(str.strip, lines[0].split('\n'))
        if '' in lines:
            lines = lines[:lines.index('')]
        return lines

    def parse_conditions(self):
        """Parse the conditions from the rule function docstring"""
        return self._parse_multiline('(?<=Conditions:\n).*')

    def parse_notes(self):
        """Parse any notes from the rule function docstring"""
        return ' '.join(self._parse_multiline('(?<=Note: ).*'))

    def parse_footnotes(self):
        """Parse any footnotes from the rule function docstring"""
        return ' '.join(self._parse_multiline('(?<=\*).*'))

    def parse_cases(self):
        """Determine the default relevant cases for performance"""
        datasets = ('PHMRC', 'NHMRC')
        maternal = (
            'Hypertensive Disorder',
            'Other Pregnancy-Related Deaths',
            'Hemorrhage',
            'Sepsis',
            'Anemia',
        )
        pred = self.prediction
        if not isinstance(self.module, basestring):
            cases = itertools.product(datasets, map(str.title, self.module))
        elif isinstance(pred, basestring) and pred in maternal:
            cases = itertools.product(datasets, [pred.split()[0], 'Maternal'])
        else:
            cases = datasets
        return map(lambda x: '-'.join(x), cases)

    def get_questions(self, module=None):
        # If there is only one set of survey questions
        if isinstance(self.questions, dict):
            return self.questions

        # There are different sets of survey questions for different modules
        if not module:
            module = self.module[0]
        return self.questions[self.module.index(module)]

    def evaluate(self, df, module=None):
        """Evaluate the rule on a dataframe return a series of endorsements"""
        if not module:
            module = self.module[0]
        questions = self.get_questions(module)

        def wrapper(series):
            return self.func(**{fn_param: series.loc[question]
                                for fn_param, question in questions.items()
                                if question in series})
        return df.apply(wrapper, axis=1)
