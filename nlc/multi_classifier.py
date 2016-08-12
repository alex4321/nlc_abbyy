from .base_classifier import BaseClassifier


class MultiClassifier(BaseClassifier):
    """
    Classifier will use one NLC and return to other if it's throws error.
    E.g. you can use some network NLC (e.g. Watson)
      and switch back to simple local NLC if it not available
    """

    def __init__(self, front_classifier, back_classifier):
        """
        Initialize multiclassifier
        :param front_classifier: first NLC
        :type front_classifier: dict|BaseClassifier
        :param back_classifier: other NLC. Will be used if first throws error
        :type back_classifier: dict|BaseClassifier
        """
        if isinstance(front_classifier, BaseClassifier):
            self._front = front_classifier
        else:
            self._front = BaseClassifier.from_config(front_classifier)
        if isinstance(back_classifier, BaseClassifier):
            self._back = back_classifier
        else:
            self._back = BaseClassifier.from_config(back_classifier)

    def train(self, classes, verbose=False):
        self._front.train(classes, verbose)
        self._back.train(classes, verbose)

    def classify(self, text):
        try:
            return self._front.classify(text)
        except Exception as e:
            print(e)
            return self._back.classify(text)

    def _get_config(self):
        return {
            'front_classifier': self._front.config,
            'back_classifier': self._back.config
        }
