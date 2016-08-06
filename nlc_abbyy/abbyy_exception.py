class ABBYYException(Exception):
    def __init__(self, code, message, *args, **kwargs):
        """
        Initialize exception
        :param code: return code
        :type code: int
        :param message: message
        :type message: str
        """
        self.code = code
        self.message = message
        super(ABBYYException, self).__init__(*args, **kwargs)

    def __str__(self):
        return "ABBYY SmartClassifier exception : {0}.\nReturn code {1}".format(
            self.message, self.code
        )

    def __repr__(self):
        return str(self)
