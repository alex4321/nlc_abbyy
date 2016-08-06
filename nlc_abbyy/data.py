from .language import Language


class Data:
    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)


class ClassifiedCategoriesData(Data):
    def __init__(self, probability, is_confident, category_id):
        self.probability = probability
        self.is_confident = is_confident
        self.category_id = category_id


class DocumentData(Data):
    def __init__(self, data):
        self.name = data["Name"]
        self.error = data["Error"]
        self.warnings = [
            item["LocalizedMessages"]
            for item in data["Warnings"]
            ]
        self.classified_categories = [
            ClassifiedCategoriesData(category["Probability"], category["IsConfident"], category["CategoryId"])
            for category in data["ClassifiedCategories"]
            ]


class ProjectConfiguration(Data):
    def __init__(self, name, language, use_semantics, inclusiveness):
        self.name = name
        self.language = Language(language)
        self.use_sematics = use_semantics
        self.inclusiveness = inclusiveness


class ProjectData(Data):
    def __init__(self, data):
        """
        Initialize data
        :param data: dict
        :type data: dict
        """
        self.id = data["Id"]
        self.configuration = ProjectConfiguration(
            data["Configuration"]["Name"],
            data["Configuration"]["Language"],
            data["Configuration"]["UseSemantics"],
            data["Configuration"]["Inclusiveness"]
        )
        self.created_timestamp = data["CreatedTimestamp"]
        self.deployed_timestamp = data["DeployedTimestamp"]
        self.is_model_only = data["IsModelOnly"]
        self.control_fmeasure = 1.0
        self.train_fmeasure = 1.0
        if "ModelInfo" in data:
            if "ControlSetInfo" in data["ModelInfo"]:
                control_set_info = data["ModelInfo"]["ControlSetInfo"]
                if control_set_info and "FMeasure" in control_set_info:
                    self.control_fmeasure = control_set_info["FMeasure"]
            if "TrainingSetInfo" in data["ModelInfo"]:
                training_set_info = data["ModelInfo"]["TrainingSetInfo"]
                if training_set_info and "FMeasure" in training_set_info:
                    self.train_fmeasure = training_set_info["FMeasure"]


class JobData(Data):
    def __init__(self, data):
        """
        Initialize job data
        :param data: data
        :type data: dict
        """
        self.id = data["Id"]
        self.project_id = data["ProjectId"]
        self.started = data["Started"]
        self.finished = data["Finished"]
        self.status = data["Status"]
        self.progress = data["Progress"]
        self.error = data["Error"]
        self.type = data["Type"]
        self.warnings = [
            warning["LocalizedMessages"]
            for warning in data["Warnings"]
            ]


class CategoryData(Data):
    def __init__(self, data):
        self.id = data["Id"]
        self.parent_id = data["ParentId"]
        self.name = data["Configuration"]["Name"]
