import json 
import numpy as np
import random
import spacy
import time
import ListenAndSpeak
from ListenAndSpeak import Ios, Analyzer, Cancel

class ElaborateAnswer():
            
    def __init__(self, ios, analyzer):
        self.ios = ios
        self.analyzer = analyzer
        with open('intents.json') as file:
            self.data = json.load(file)
        
        self.tagToFunction = {
            "booking" : Booking(),
            "checkIn" : CheckIn(),
            "key" : Key(),
            "cost" : Cost(),
            "taxi" : Taxi(),
            "alarm" : Alarm(),
        }

    
    def execute(self, tag, sentence):
        print(tag)
        try:
            answer = self.tagToFunction[tag](self.analyzer, self.ios, sentence)
        except KeyError:
            for i in self.data['intents']:
                if i['tag'] == tag:
                    answer = np.random.choice(i['responses'])
        return (answer, not tag=="bye")

class Booking():
    def __call__(self, analyzer, ios, sentence):
        room2cost = {"single" : 40,"double" : 60,"quadruple" : 100,"suite" : 200, "sweet" : 200}
        dep = analyzer.dep(sentence)
        room = None
        if "dobj" in dep.keys():
            if dep["dobj"].text in room2cost.keys(): room = dep["dobj"]
            else:
                for child in dep["dobj"].children:
                    if child.text in room2cost.keys():
                        room = child.text
        ent = analyzer.entity(sentence)
        nights = None
        print(ent)
        if "DATE" in ent.keys():
            nights = analyzer.elaborate_date(ent["DATE"], sentence)
        i = 0
        while room is None:
            if i>5: return "I canceled the operation, what can I do for you?"
            if i==0: ios.speak("What type of room do you want? We have single, double, quadruple or suite available.")
            else: ios.speak("Can you repeat, What type of room do you want? Single, double, quadruple or suite?")
            sentence = ios.listen()
            if analyzer.word_search("cost", sentence):
                cost = Cost()
                cost(analyzer, ios, sentence)
                continue
            for t in room2cost.keys():
                if t in sentence: room = t
            i+=1
        if room == "sweer": room = "suite"
        i=0
        while nights is None:
            if i>5: return "I canceled the operation, what can I do for you?"
            if i==0: ios.speak("How many nights do you want to stay with us?")
            else: ios.speak("Can you repeat, How many nights do you want to stay with us?")
            sentence = ios.listen()
            if analyzer.word_search("cost", sentence):
                cost = Cost()
                cost(analyzer, ios, sentence, room)
                continue
            i+=1
            ent = analyzer.entity(sentence)
            print(ent)
            if "DATE" in ent.keys():
                nights = analyzer.elaborate_date(ent["DATE"], sentence)
            elif "CARDINAL" in ent.keys():
                if ent["CARDINAL"][0].text == "two": nights = 2
                else: nights = int(ent["CARDINAL"][0].text)

        euro = nights*room2cost[room]
        i = 0
        while True:
            if i>5: return "I canceled the operation, what can I do for you?"
            if i==0: ios.speak(f"Ok, I'm booking you a {room} for {nights} nights. The total amount is {euro} euro. You confirm?")
            else: ios.speak(f"Can you repeat, You confirm a booking for a {room} for {nights} nights for {euro}?")
            sentence = ios.listen()
            response = analyzer.yes_or_no(sentence)
            i+=1
            if response is None: 
                continue
            if not response: return "I canceled the operation, what can I do for you?"
            else: break
        check = CheckIn()
        check(analyzer, ios, ".")
        return "Tell me if I can do something else for you."
   

class CheckIn():
    def __call__(self, analyzer, ios, sentence):
        name = analyzer.name(sentence)
        i = 0
        while name is None:
            if i>3: return "I canceled the operation, what can I do for you?"
            if i==0: ios.speak("Ok, let's proceed with the check in. Can I have your name and surname?")
            else: ios.speak("Can you repeat, what is your name and surname?")
            i+=1
            sentence = ios.listen()
            name = analyzer.name(sentence)
        roomNumber = random.randint(0, 30) + random.randint(1, 5)*100
        ios.speak(f"Ok, you have room number {roomNumber}. take this key. enjoy your stay")
        return "For anything else I am at your disposal"


class Key():
    def __call__(self, analyzer, ios, sentence):
        pos = analyzer.pos(sentence)
        i = 0
        while not "NUM" in pos.keys():
            if i>3: return "I canceled the operation, what can I do for you?"
            if i==0: ios.speak("You want your key room. What is your key number?")
            else: ios.speak("Can you repeat, what is your key numeber?")
            sentence = ios.listen()
            pos = analyzer.pos(sentence)
            i+=1
        number = pos["NUM"].text
        ios.speak("Wait a moment please...")
        #Some other control
        time.sleep(1)
        ios.speak(f"ok, take the key to room {number}")
        return "For anything else I am at your disposal"

class Cost():
    def __call__(self, analyzer, ios, sentence, r = None):
        room2cost = {"single" : 40,"double" : 60,"quadruple" : 100,"suite" : 200}
        
        dep = analyzer.dep(sentence)
        room = r
        if "dobj" in dep.keys():
            if dep["dobj"].text in room2cost.keys(): room = dep["dobj"]
            else:
                for child in dep["dobj"].children:
                    if child.text in room2cost.keys():
                        room = child.text
        i=0
        while room is None:
            if i>5: return "I canceled the operation, what can I do for you?"
            if i==0: ios.speak("What type of room you want to know the cost of? We have single, double, quadruple or suite available.")
            else: ios.speak("Can you repeat, What type of room you want to know the cost of? Single, double, quadruple or suite?")
            sentence = ios.listen()
            for t in room2cost.keys():
                if t in sentence: room = t
            i+=1
        ios.speak(f"A {room} cost {room2cost[room]} euros per night")
        return "Tell me something else"
        
class Taxi():
    def __call__(self, analyzer, ios, sentence):
        dep = analyzer.dep(sentence)
        if "prep" in dep.keys() and dep["prep"].text=='to': where = list(dep["prep"].children)[0]
        else: where = None
        i = 0
        while where is None:
            if i>3: return "I canceled the operation, what can I do for you?"
            if i==0: ios.speak("Ok, i'll call a taxi. What is the destiation?")
            else: ios.speak("Can you repeat, what is the destination?")
            sentence = ios.listen()
            pos = analyzer.pos(sentence)
            if "NOUN" in pos.keys(): where = pos["NOUN"]
            i+=1
        ios.speak("Wait a moment please...")
        time.sleep(1)
        ios.speak(f"ok, in 5 minutes a taxi will arrive and take you to the {where}")
        return "For anything else I am at your disposal"

class Alarm():
    def __call__(self, analyzer, ios, sentence):
        orary = analyzer.orary(sentence)
        i=0
        while orary is None:
            if i>5: return "I canceled the operation, what can I do for you?"
            if i==0: ios.speak("Ok, what time do you want to be woken up?")
            else: ios.speak("Can you repeat, what time do you want to be woken up?")
            sentence = ios.listen()
            orary = analyzer.orary(sentence)
            i+=1
        ios.speak(f"Ok, at {orary} i will call you in internal telephone")
        return "For anything else I am at your disposal"







