import os
from nlc import BaseClassifier
from collections import OrderedDict
from .abbyy_network import AbbyyNetwork
from .language import Language
from .abbyy_exception import ABBYYException


class ABBYYClassifier(BaseClassifier):
    _MAX_CLASSIFICAATION_DOCUMENTS = 100

    def __init__(self, auth, endpoint,
                 classifier_id=None, new_classifier=None):
        """
        Initialize classifier
        :param auth: login, password
        :type auth: tuple[str, str]
        :param endpoint: endpoint
        :type endpoint: str
        :param classifier_id: NLC id
        :type classifier_id: str|NoneType
        :param new_classifier: new classifier data
        :type new_classifier: dict|NoneType
        """
        assert (classifier_id is None) ^ (new_classifier is None)
        username, password = auth
        self._abbyy = AbbyyNetwork(username, password, endpoint)
        if classifier_id is not None:
            self.id = classifier_id
        else:
            name = new_classifier['name']
            language = new_classifier['language']
            if not isinstance(language, Language):
                language = Language(language)
            use_semantics = new_classifier['use_semantics']
            inclusiveness = new_classifier['inclusiveness']
            self.id = self._abbyy.create_classifier(name, language, use_semantics, inclusiveness)

    def _wait_for_job_completion(self, job_id):
        """
        Wait until job will be completed
        :param job_id: job id
        :type job_id: str
        """
        while True:
            jobs = self._abbyy.jobs()
            job = jobs[job_id]
            if job.status == 'Completed':
                break
            if job.error:
                raise ABBYYException(0, job.error)

    def train(self, classes, verbose=False):
        """
        Upload train data
        :param classes: class examples
        :type classes: dict[str, list[str]]
        :param verbose: verbose?
        :type verbose: bool
        """
        path = self._abbyy.classes_zip(classes)
        if verbose:
            print("Train classes .zip path : {0}".format(path))
        job_id = self._abbyy.upload_train_set(self.id, path)
        if verbose:
            print("Train job id : {0}".format(job_id))
        os.remove(path)
        if verbose:
            print("Train zip {0} removed".format(path))
        self._wait_for_job_completion(job_id)
        if verbose:
            print("Train job completed")
        self._abbyy.publish(self.id)

    def test(self, classes, verbose=False):
        """
        Upload test set and return error value
        :param classes: class examples
        :type classes: dict[str, list[str]]
        :param verbose: verbose?
        :type verbose: bool
        :return: F-Measure error
        :rtype: float
        """
        path = self._abbyy.classes_zip(classes)
        if verbose:
            print("Test classes .zip path : {0}".format(path))
        job_id = self._abbyy.upload_test_set(self.id, path)
        if verbose:
            print("Test job id : {0}".format(job_id))
        os.remove(path)
        if verbose:
            print("Test zip {0} removed".format(path))
        self._wait_for_job_completion(job_id)
        if verbose:
            print("Test job completed")
        classifier = self._abbyy.classifiers()[self.id]
        return 1 - classifier.control_fmeasure

    def classify(self, text):
        """
        Classify text
        :param text: text
        :type text: str
        :return: classification result
        :rtype: OrderedDict[str, float]
        """
        def class_confidence_pair_comparer(pair):
            _, conf = pair
            return conf

        name = self._abbyy.classifier_document_name(text)
        documents = self._abbyy.documents(self.id)
        if name not in documents:
            self._wait_for_job_completion(self._abbyy.upload_classifier_document(self.id, text))
            self._wait_for_job_completion(self._abbyy.classify_documents(self.id))
            documents = self._abbyy.documents(self.id)
        if len(documents) > ABBYYClassifier._MAX_CLASSIFICAATION_DOCUMENTS:
            self._abbyy.clear_sets(self.id, classification=True)
        document = documents[name]
        categories = self._abbyy.categories(self.id)
        class_confidence_pairs = []
        for classified_category in document.classified_categories:
            category_name = categories[classified_category.category_id].name
            confidence = classified_category.probability
            class_confidence_pairs.append((category_name, confidence,))
        class_confidence_pairs.sort(key=class_confidence_pair_comparer, reverse=True)
        result = OrderedDict()
        for item in class_confidence_pairs:
            class_name, confidence = item
            result[class_name] = confidence
        return result

    def _get_config(self):
        return {
            'auth': (self._abbyy.username, self._abbyy.password,),
            'endpoint': self._abbyy.endpoint,
            'classifier_id': self.id
        }

BaseClassifier.register('abbyy', ABBYYClassifier)
