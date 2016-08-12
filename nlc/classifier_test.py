import unittest
from nlc import BaseClassifier
import numpy
import math


class ClassifierTest(unittest.TestCase):
    def setUp(self):
        classes = {
            "capabilities": [
                "can you turn on the radio", "help", "help me",
                "How are you going to help me?", "how can you help me",
                "need help", "tell me what you can do", "What are you",
                "what are you capable of", "what are your capabilities Watson?",
                "what can I do", "What can i say", "what can you do",
                "what can you do for me", "what can you help me with",
                "what do you know", "what else", "what things can you do"
            ],
            "locate_amenity": [
                "Amenities", "can you find a good place to eat?",
                "can you find the nearest gas station for me",
                "find a restaurant", "Find best gas option", "find me a restaurant",
                "get me directions", "I am hungry", "I'd like to get something to eat",
                "i'm hungry", "im hungry I want to eat something", "i need some coffee",
                "i need to stop for gas", "Information on locations near me", "I want a bar",
                "i want drink", "I want eat", "i want pizza", "I want to eat pizza",
                "I want to stop for some food", "let's get some grub", "locate ammenity",
                "Navigation", "nearby restaurant", "order a pizza", "pizza", "restaurant",
                "restaurants", "show me the best path", "Stop for food/coffee",
                "where are the closest restrooms", "where can i drink", "where can i eat pizza?",
                "where can i have pizza", "where is a restaurant", "where is ATM",
                "where is the bathroom?", "where is the pool", "where's the nearest exit"
            ]
        }
        self.classifier = self.build_classifier()
        self.classifier.train(classes, verbose=True)

    def build_classifier(self):
        raise NotImplementedError()

    def test_classifier(self):
        classes = {
            'capabilities': [
                'so, what your current version can do?',
                'what\'s your abilities?', 'can switch off phone?'
            ],
            'locate_amenity': [
                'find restaurants or something like it', 'what places you know?',
                'search for hotels'
            ]
        }
        print("Total test error : ", self.classifier.test(classes, True))

    def test_config(self):
        config = self.classifier.config
        instantitated_classifier = BaseClassifier.from_config(config)
        self.assertEqual(
            self.classifier.classify('so, what your current version can do?'),
            instantitated_classifier.classify('so, what your current version can do?')
        )
        self.assertEqual(
            self.classifier.classify('find restaurants or something like it'),
            instantitated_classifier.classify('find restaurants or something like it')
        )

    def test_synonyms(self):
        classes = self.classifier.classify("Look for a cafe")
        print(classes)
        self.assertTrue(classes['locate_amenity'] > 0.6)
        self.assertTrue(classes['capabilities'] <= 0.6)

    def test_nothing(self):
        classes = self.classifier.classify("You can't test this")
        print(classes)
        self.assertTrue(classes['locate_amenity'] <= 0.6)
        self.assertTrue(classes['capabilities'] <= 0.6)
