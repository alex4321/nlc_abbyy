from .language import Language
from subprocess import Popen, PIPE
import json
import zipfile
import tempfile
import os
from .data import *
from .abbyy_exception import ABBYYException
import threading
from transliterate import translit


_LOCK = threading.Lock()

class AbbyyNetwork:
    def __init__(self, username, password, endpoint):
        """
        Initialize ABBYY SmartClassifier
        :param username: username
        :type username: str
        :param password: password
        :type password: str
        :param endpoint: API endpoint
        :type endpoint: str
        """
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.auth_cookie = self._login()

    def _command(self, uri, args):
        """
        Return CURL output or throw error
        :param uri: uri
        :type uri: str
        :param args: CURL extra args
        :type args: list[str]
        :return: output
        :rtype: str
        """
        command = [
            'curl', '-s', '-u', '{0}:{1}'.format(self.username, self.password),
            self.endpoint + '/' + uri
        ] + args
        with _LOCK:
            popen = Popen(command, stdout=PIPE, stderr=PIPE)
        output, error = popen.communicate()
        if popen.returncode != 0:
            raise ABBYYException(popen.returncode, error.decode())
        return output.decode()

    def _login(self):
        """
        Get login cookies
        :return: cookies
        :rtype: dict[str, str]
        """
        cookies = self._command('/api/account/login', [
            '--cookie-jar', '-',
            '-H', 'X-Compress: null',
            '-H', 'Content-Type: application/json;charset=UTF-8',
            '-H', 'Accept: application/json, text/plain, */*',
            '--data-binary', json.dumps({
                'username': self.username,
                'password': self.password,
                'isPersistent': True,
                'accountType': 'custom'
            })])
        lines = cookies.split('\n')
        result = {}
        for line in lines:
            parts = [part for part in line.split('\t') if part != '']
            if len(parts) >= 7:
                name = parts[5]
                value = parts[6]
                result[name] = value
        return result

    def classifiers(self):
        """
        Get classifiers
        :return: classifiers dict
        :rtype: dict[str, ProjectData]
        """
        json_code = self._command('api/projects', [
            '-H', 'Content-Type: application/json;charset=UTF-8',
            '-H', 'Accept: application/json, text/plain, */*'
        ])
        data = json.loads(json_code)
        classifiers = {}
        for item in data:
            classifier = ProjectData(item)
            classifiers[classifier.id] = classifier
        return classifiers

    def jobs(self):
        """
        Get jobs
        :return: jobs
        :rtype: dict[str, JobData]
        """
        data = json.loads(self._command('api/jobs', [
            '-H', 'Accept: application/json, text/plain, */*'
        ]))
        jobs = {}
        for item in data:
            job = JobData(item)
            jobs[job.id] = job
        return jobs

    def create_classifier(self, name, language, use_semantics, inclusiveness):
        """
        Create NLC
        :param name: NLC name
        :type name: str
        :param language: NLC language
        :type language: Language
        :param use_semantics: use only text signs or semantic?
        :type use_semantics: bool
        :param inclusiveness: 0 - faster, 1 - balance, 2 - quality
        :type inclusiveness: int
        :return: NLC id
        :rtype: str
        """
        assert name != ""
        assert 0 <= inclusiveness <= 2
        return json.loads(self._command('api/projects', [
            '-H', 'Content-Type: application/json;charset=UTF-8',
            '-H', 'Accept: application/json, text/plain, */*',
            '--data-binary', json.dumps({
                'name': name,
                'language': language.value,
                'useSemantics': use_semantics,
                'inclusiveness': inclusiveness
            })
        ]))

    def classes_zip(self, classes):
        """
        Build classes zip file
        :param classes: class examples
        :type classes: dict[str, list[str]]
        :return: path to zip file
        :rtype: str
        """
        path = tempfile.mktemp('.classes.zip')
        zf = zipfile.ZipFile(path, 'w')
        for class_name, examples in classes.items():
            for i, example in enumerate(examples):
                zf.writestr(class_name + '/' + str(i) + '.txt', example)
        zf.close()
        return path

    def _import_set(self, project_id, set_path, type):
        """
        Set set from zip file
        :param project_id: project id
        :type project_id: str
        :param set_path: train set zip path (see classes_zip)
        :type set_path: str
        :param type: set type (trainingSet/controlSet)
        :type type: str
        :return: work id
        :rtype: str
        """
        _, fname = os.path.split(set_path)
        work_id = json.loads(self._command(
            'api/projects/{0}/{1}/import?runNextStep=true'.format(project_id, type), [
                '-H', 'Content-Type: multipart/form-data',
                '-H', 'X-Compress: null',
                '-H', 'Accept: */*',
                '-F', 'name={0}'.format(fname),
                '-F', 'file=@{0}'.format(set_path)]))
        return work_id

    def upload_train_set(self, project_id, set_path):
        """
        Set train set from zip file
        :param project_id: project id
        :type project_id: str
        :param set_path: train set zip path (see classes_zip)
        :type set_path: str
        :return: work id
        :rtype: str
        """
        return self._import_set(project_id, set_path, 'trainingSet')

    def upload_test_set(self, project_id, set_path):
        """
        Set test set from zip file
        :param project_id: project id
        :type project_id: str
        :param set_path: train set zip path (see classes_zip)
        :type set_path: str
        :return: work id
        :rtype: str
        """
        return self._import_set(project_id, set_path, 'controlSet')

    def publish(self, project_id):
        """
        Publish project
        :param project_id: project id
        :type project_id: str
        """
        self._command('api/projects/{0}/deploy'.format(project_id), [
            '-X', 'POST', '-H', 'Accept: application/json, text/plain, */*',
            '-H', 'Content-Length: 0'])

    def classifier_document_name(self, content):
        """
        Get classifier document name by content
        :param content: request to classify
        :type content: str
        :return: document file name
        :rtype: str
        """
        return translit(''.join([char for char in content if char.isalpha()]) + '.txt', reversed=True)

    def upload_classifier_document(self, project_id, content):
        """
        Upload domument for classification
        :param project_id: project id
        :type project_id: str
        :param content: document text
        :type content: str
        :return: job id
        :rtype: str
        """
        auth_cookie = ""
        for cookie_name, cookie_value in self.auth_cookie.items():
            auth_cookie += "{0}={1}; ".format(cookie_name, cookie_value)
        fname = self.classifier_document_name(content)
        temp_path = tempfile.mkdtemp()
        temp = os.path.join(temp_path, fname)
        with open(temp, 'w') as f:
            f.write(content)
        try:
            answer = json.loads(self._command('api/projects/{0}/classificationSet/documents/import'.format(project_id), [
                '-H', 'Cookie: {0}'.format(auth_cookie),
                '-H', 'X-Compress: null',
                '-H', 'Content-Type: multipart/form-data',
                '-H', 'Accept: */*',
                '-H', 'Connection: keep-alive',
                '-F', 'name={0}'.format(fname),
                '-F', 'file=@{0}'.format(temp)]))
        except Exception as e:
            raise e
        finally:
            os.remove(temp)
            #TODO: remove directory too
        if isinstance(answer, dict):
            raise ABBYYException(0, answer["ErrorMessage"])
        else:
            return answer

    def classify_documents(self, project_id):
        """
        Classify uploaded documents
        :param project_id: project id
        :type project_id: str
        :return: job id
        :rtype: str
        """
        return json.loads(self._command('api/projects/{0}/classifying'.format(project_id), [
            '-X', 'POST', '-H', 'Accept: application/json, text/plain, */*',
            '-H', 'Content-Length: 0']))

    def documents(self, project_id):
        """
        Get documents data
        :param project_id: project id
        :type project_id: str
        :return: documents
        :rtype: dict[str, DocumentData]
        """
        documents = [DocumentData(item) for item in json.loads(self._command('api/projects/{0}/classificationSet/documents'.format(project_id), [
            '-H', self.auth_cookie,
            '-H', 'X-Compress: null',
            '-H', 'Accept: application/json, text/plain, */*']))]
        result = {}
        for item in documents:
            result[item.name] = item
        return result

    def categories(self, project_id):
        """
        Get categories
        :param project_id: project id
        :type project_id: str
        :return: categories
        :rtype: dict[int, CategoryData]
        """
        categories = [CategoryData(item) for item in json.loads(self._command('api/projects/{0}/categories'.format(project_id), [
            '-H', self.auth_cookie,
            '-H', 'Accept: application/json, text/plain, */*']))]
        result = {}
        for category in categories:
            result[category.id] = category
        return result

    def clear_sets(self, project_id, classification=False, control=False, training=False):
        """
        Clear sets
        :param project_id: project id
        :type project_id: str
        :param classification: clear classification srt?
        :type classification: bool
        :param control: clear control set?
        :type control: bool
        :param training: clear training set?
        :type training: bool
        """
        bool2str = {True:'true', False:'false'}
        uri = 'api/projects/{0}/clear?clearClassificationSet={1}&clearControlSet={2}&clearTrainingSet={3}'\
            .format(project_id, bool2str[classification], bool2str[control], bool2str[training])
        self._command(uri, [
            '-X', 'POST',
            '-H', self.auth_cookie,
            '-H', 'Accept: application/json, text/plain, */*',
            '-H', 'Content-Length: 0'])
