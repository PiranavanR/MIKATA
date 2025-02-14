import sys
import pyttsx3

def init_engine():

    engine = pyttsx3.init()

    engine.setProperty('rate', 175)

    engine.setProperty('pitch', 2)
    
    return engine

def say(q):

    engine.say(q)
    
    engine.runAndWait()

engine = init_engine()

say(str(sys.argv[1]))
