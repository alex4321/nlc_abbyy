from collections import OrderedDict
import copy
import numpy
import math


class BaseClassifier:
    """
    Base classifier class
    """
    _classes = {}

    def train(self, classes, verbose=False):
        """
        Train NLC
        :param classes: classes
        :type classes: dict[str, list[str]]
        :param verbose: verbose
        :type verbose: bool
        """
        raise NotImplementedError()

    def classify(self, text):
        """
        Classify text
        :param text: text
        :type text: str
        :return: classes
        :rtype: OrderedDict[str, float]
        """
        raise NotImplementedError()

    @staticmethod
    def register(name, cls):
        """
        Register NLC class
        :param name: name (to use in config dicts)
        :type name: str
        :param cls: class
        :type cls: class
        """
        BaseClassifier._classes[name] = cls

    @property
    def config(self):
        """
        Get config
        :return: configuration dict
        :rtype: dict
        """
        cls = self.__class__
        cfg = cls._get_config(self)
        for class_name, class_object in BaseClassifier._classes.items():
            if class_object == cls:
                cfg['class'] = class_name
        return cfg

    def _get_config(self):
        """
        Get config
        :return: configuration dict
        :rtype: dict
        """
        raise NotImplementedError()

    @staticmethod
    def from_config(config):
        """
        Get classifier instance from config
        :param config: config
        :type config: dict
        :return: classifier
        :rtype: BaseClassifier
        """
        cls = BaseClassifier._classes[config['class']]
        cfg = copy.deepcopy(config)
        del cfg['class']
        return cls(**cfg)

    def test(self, classes_examples, verbose=False):
        """
        Get test result (mean-square error)
        :param classes_examples: class examples
        :type classes_examples: dict[str, list[str]]
        :param verbose: verbose
        :type verbose: bool
        :return: error
        :rtype: float
        """
        errors = []
        for class_name, examples in classes_examples.items():
            for example in examples:
                classified_classes = self.classify(example)
                if verbose:
                    print(example, classified_classes)
                right = []
                real = []
                for classified_class, confidence in classified_classes.items():
                    if classified_class == class_name:
                        right.append(1.0)
                    else:
                        right.append(0.0)
                    if confidence > 0.6:
                        real.append(1.0)
                    else:
                        real.append(0.0)
                    errors += (numpy.array(right) - numpy.array(real)).tolist()
        error = numpy.sum(numpy.array(errors) * numpy.array(errors) / len(errors))
        return error
