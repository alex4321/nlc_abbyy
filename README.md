Basics
------
This is implementation of BaseClassifier interface from 
https://github.com/alex4321/nlc, that uses [Abbyy SmartClassifier](https://www.abbyy.com/en-us/smartclassifier/) as backend.
Currently supports English/Russian languages. Need installed [curl](https://en.wikipedia.org/wiki/CURL)

Installation
------------
Firstly, you need installed CURL in PATH environment variable.
In linux - use packages manager. In debian-based distro it can be installed via

```
# apt-get install curl
```

In Windows - you can use [MinGW](http://www.mingw.org/) and add binaries path to PATH environment variable.

Also, you need ```transliterate``` library :
```
# pip install transliterate 
```

Example
-------
English example here
```
#!/bin/env python3
import os
from nlc_abbyy import ABBYYClassifier, Language


username = os.environ['ABBYY_USERNAME']
password = os.environ['ABBYY_PASSWORD']
classifier = ABBYYClassifier((username, password,), 'http://infoextractorapitest.abbyy.com/classifier',
                             new_classifier={
                                 'name': 'TestNlcProjectFromPython',
                                 'language': Language.english,
                                 'use_semantics': True,
                                 'inclusiveness': 1
                             })
print("New classifier id is {0}".format(classifier.id))
classifier.train({
    "capabilities": [
        "can you turn on the radio", "help", "help me",
        "How are you going to help me?", "how can you help me",
        "need help", "tell me what you can d o", "What are you",
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
}, verbose=True)
print("Test set error {0}".format(classifier.test({
    'capabilities': [
        'so, what your current version can do?',
        'what\'s your abilities?', 'can switch off phone?'
    ],
    'locate_amenity': [
        'find restaurants or something like it', 'what places you know?',
        'search for hotels'
    ]
}, verbose=True)))
print(classifier.classify('so, what your current version can do?'))
print(classifier.classify('find restaurants or something like it'))
print(classifier.config)
```
That example must give something like next:
```
New classifier id is a365d1a9-c9ff-4399-ae85-01ced7e79428
Train classes .zip path : C:\Users\GAUSS~1.DES\AppData\Local\Temp\tmptdnbkele.classes.zip
Train job id : 60923968-43a3-4a2e-9746-a9a7672b9578
Train zip C:\Users\GAUSS~1.DES\AppData\Local\Temp\tmptdnbkele.classes.zip removed
Train job completed
Test classes .zip path : C:\Users\GAUSS~1.DES\AppData\Local\Temp\tmp_aghare_.classes.zip
Test job id : b83843c2-7fcd-42e5-b072-e1c043c7a537
Test zip C:\Users\GAUSS~1.DES\AppData\Local\Temp\tmp_aghare_.classes.zip removed
Test job completed
Test set error 0.03452
OrderedDict([('capabilities', 0.9948745679045183), ('locate_amenity', 0.005125432095481649)])
OrderedDict([('locate_amenity', 0.988253958329229), ('capabilities', 0.011746041670770846)])
{'class': 'abbyy', 'auth': ('alexander_test', 'alexander_testpass'), 'classifier_id': 'a365d1a9-c9ff-4399-ae85-01ced7e79428', 'endpoint': 'http://infoextractorapitest.abbyy.com/classifier'}
```
Russian example :
```
import os
from nlc_abbyy import ABBYYClassifier, Language


username = os.environ['ABBYY_USERNAME']
password = os.environ['ABBYY_PASSWORD']
classifier = ABBYYClassifier((username, password,), 'http://infoextractorapitest.abbyy.com/classifier',
                             new_classifier={
                                 'name': 'TestNlcProjectFromPython_ru',
                                 'language': Language.russian,
                                 'use_semantics': True,
                                 'inclusiveness': 1
                             })
print("New classifier id is {0}".format(classifier.id))
classifier.train({
    "capabilities": [
        "можешь выключить радио?", "помоги", "помоги мне",
        "Чем ты можешь быть полезен?", "Как ты можешь мне помочь?",
        "Нужна помощь", "Скажи, что ты можешь", "Какие у тебя возможности?",
        "Что я могу сделать?", "Что я могу сказать", "Что ты можешь?",
        "Что ты можешь сделать?", "С чем ты можешь помочь?",
        "Что ты знаешь?", "Что ещё?", "Какие вещи ты можешь?"
    ],
    "locate_amenity": [
        "Удобства", "найди, где перекусить?",
        "найди заправочную станцию", "найди ресторан",
        "выбери заправочную станцию", "выбери ресторан",
        "куда ехать?", "Найди кафе", "Выбери кафе",
        "Найди гостиницу", "Выбери гостиницу",
        "Какие заправочные станции рядом?", "Покажи заправочные станции"
    ]
}, verbose=True)
print("Test set error {0}".format(classifier.test({
    'capabilities': [
        'что твоя текущая версия может?',
        'можешь отключить телефон?'
    ],
    'locate_amenity': {
        'какие кафе рядом?'
    }
}, verbose=True)))
print(classifier.classify('что твоя текущая версия может?'))
print(classifier.classify('можешь отключить телефон'))
print(classifier.config)
```
