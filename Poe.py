import numpy as np
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder

import pickle

import ListenAndSpeak
from ListenAndSpeak import Ios, Analyzer, Cancel
import tagToFunction
from tagToFunction import ElaborateAnswer



ios = Ios()
analyzer = Analyzer()
def chat():
    # load trained model
    model = keras.models.load_model('chat_model')

    # load tokenizer object
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # load label encoder object
    with open('label_encoder.pickle', 'rb') as enc:
        lbl_encoder = pickle.load(enc)

    # parameters
    max_len = 20
    
    done = True
    
    elaborate = ElaborateAnswer(ios, analyzer)
    
    while done:
        inp = ios.listen() #Prendi input da voce
        result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp]),
                                             truncating='post', maxlen=max_len))
        print(result)
        max = np.max(result)
        print(max)
        if max < 0.6:
            ios.speak("Sorry, I can't solve this problem. Ask me for something different.")
            continue
        tag = lbl_encoder.inverse_transform([np.argmax(result)])
        try:
            answer, done = elaborate.execute(tag[0], inp)
        except Cancel:
            print("Cancelled!")
            ios.speak("Ok, What can I do for you?")
            continue
        
        ios.speak(answer)

print("Start")
chat()