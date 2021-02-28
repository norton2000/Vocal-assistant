import speech_recognition as sr
from gtts import gTTS 
import os 
import spacy
import datetime
from spacy import displacy

class Ios():
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def recognize_speech_from_mic(self):

        if not isinstance(self.recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(self.microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            response["transcription"] = self.recognizer.recognize_google(audio)
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech"

        return response

    def listen(self, PROMPT_LIMIT=10):
        for j in range(PROMPT_LIMIT):
            print('Speak Now!')
            guess = self.recognize_speech_from_mic()
            if guess["transcription"]:
                break
            if not guess["success"]:
                break
            print("I didn't catch that. What did you say?\n")
        
        if guess["error"]:
            print("ERROR: {}\n".format(guess["error"]))
            return None
        
        print(f'You say: {guess["transcription"]}')
        return guess["transcription"]

    def speak(self, output):
        language = 'en'
        myobj = gTTS(text=output, lang=language, slow=False) 
        myobj.save("welcome.mp3") 
        os.system("mpg321.exe welcome.mp3")
    

class Analyzer():
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        
    def analyze(self, text):
        self.quit(text)
        doc = self.nlp(text)
        sentences = list(doc.sents)
        deps, poss = {}, {}
        i = 0
        displacy.render(doc, style="dep")
        for sentence in sentences:
            dep, pos = {}, {}
            root = sentence.root
            dep['root'] = root
            pos[root.pos_] = root
            for child in root.children:
                if child.dep_ == 'nsubj': dep['subj'] = child
                elif child.dep_ == 'dobj': dep['obj'] = child
                else: dep[child.dep_] = child
                pos[child.pos_] = child
            deps[i] = dep
            poss[i] = pos
            i += 1
        return deps, poss
    
    def entity(self, text): 
        self.quit(text)
        doc = self.nlp(text)
        entitys = {}
        for ent in doc.ents:
            if ent.label_ in entitys.keys(): entitys[ent.label_].append(ent)
            else: entitys[ent.label_] = [ent]
        return entitys
        
    def pos(self,text):
        self.quit(text)
        doc = self.nlp(text)
        pos = {}
        for token in doc:
            pos[token.pos_] = token
        return pos
    
    def dep(self,text):
        self.quit(text)
        doc = self.nlp(text)
        dep = {}
        for token in doc:
            dep[token.dep_] = token
        return dep
        
    def pos_search(self,text,pos_label):
        pos = self.pos(text)
        if pos_label in pos.keys():
            return pos[pos_label]
        return None
    
    def word_search(self, word, text):
        self.quit(text)
        return word in text
        
    
    def elaborate_date(self, text, sentence):
        day2number = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        number = 0
        day = 0
        for elem in text:
            for word in elem:
                if word.text in day2number:
                    today = datetime.datetime.today().weekday()
                    to = day2number.index(word.text)
                    n = (to - today) % 7
                    if n == 0: n = 7
                    number += n
                    break
                if word.text == "week" or word.text == "weeks":
                    children = list(word.children)
                    if len(children) > 0:
                        if children[0].pos_ == "NUM":
                            if children[0].text == "two": number += 14
                            else: number += int(children[0].text) * 7     
                        else: number += 7
                        if len(children)>1 and children[1].text == "and":
                            and_text = sentence[sentence.index("and")+4:]
                            and_doc = self.nlp(and_text)
                            number += self.elaborate_date([and_doc], and_text)
                    else: number += 7
                    break
                if word.pos_ == "NUM":
                    if word.text == "two": day += 2
                    else: day += int(word.text)
        if number == 0: number = day
        return number if not number == 0 else None
        
    def orary(self, text):
        #Controlla prima se c'è at
        self.quit(text)
        doc = self.nlp(text)
        for token in doc:
            if token.text == "at":
                for child in token.children:
                    if child.pos_ == "pobj" and child.pos_ == "NUM":
                        return child.text
        #Altrimenti controlla se c'è un TIME
        ent = self.entity(text)
        if "TIME" in ent.keys():
            return token.text
        elif "CARDINAL" in ent.keys():
            for elem in ent["CARDINAL"]:
                for token in elem:
                    if token.pos_ == "NUM":
                        n = int(token.text)
                        if n>0 and n<24.1:
                            return token.text
        return None
    
    def name(self, text):
        ent = self.entity(text)
        if not "PERSON" in ent.keys():
            return None
        else:
            return ent["PERSON"][0].text
    
    def quit(self, text):
        if "quit" in text or "cancel" in text:
            raise Cancel
    
    def yes_or_no(self, text):
        self.quit(text)
        if "yes" in text or "ok" in text or "of course" in text or "yeah" in text: return True
        if "no" in text or "cancel" in text: return False
        return None
        
class Cancel(Exception):
    pass
            
        