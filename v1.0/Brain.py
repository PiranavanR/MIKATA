from Features import *
import requests, sys, os, json, time
from subprocess import call
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QMovie, QPixmap, QTransform, QFontDatabase, QColor
from PyQt5.QtCore import QTimer, QTime, QThread, Qt, pyqtSignal
from MikataUIv2 import Ui_MainWindow
import speech_recognition as sr
from tensorflow.keras.models import load_model # type: ignore
import pickle

os.system("pyuic5 -o MikataUIv2.py MikataUIv2.ui")

with open("Resources\Data.json", "r")as f:
    data = json.load(f)

volume_control = Volume()
weather = Weather()
web = WebControl()

class Brain(QThread):

    updateSignal = pyqtSignal(str, str)  

    def __init__(self):
        super(Brain, self).__init__()

        self.sesID = -1

        with open("Resources\conversation_history.json", "r") as f:
            self.history = json.load(f)

        self.unknown = data['re-answer']['unknown']
        self.verify = data['re-answer']['verify']

        model = load_model('Resources\\Models\\Intent\\intents.h5')

        with open('Resources\\Models\\Intent\\utils\\classes.pkl','rb') as file:
            classes = pickle.load(file)

        with open('Resources\\Models\\Intent\\utils\\tokenizer.pkl','rb') as file:
            tokenizer = pickle.load(file)

        with open('Resources\\Models\\Intent\\utils\\label_encoder.pkl','rb') as file:
            label_encoder = pickle.load(file)

        self.intent_classifier_m = IntentClassifier(classes,model,tokenizer,label_encoder)

        #self.test_intent_download()
    
    def run(self):
        self.r= sr.Recognizer()
        print("Running")
        self.mode = "chat"
        self.imode = "text"
        self.listen()
    
    def listen(self):
        if self.imode == "speech":
            with sr.Microphone(1) as source:
                self.r.adjust_for_ambient_noise(source, 1)  
                print("Say something!")
                try:
                    audio = self.r.listen(source)
                    print("Processing...")
                    query = self.r.recognize_google(audio, language='en-IN')
                    self.updateSignal.emit(query, self.mode)
                except Exception as e:
                    print(e)
                    self.listen()

    def get_response(self, query, mode):

        with open("Resources\conversation_history.json", "r") as f:
            self.history = json.load(f)
        self.history.append({"role": "user", "content": query})

        if "speech input" in query:
            if "enable" or " on " in query:
                self.imode = "speech"
                return "Mikata: Speech input enabled."
            elif "disable" or " off " in query:
                self.imode = "text"
                return "Mikata: Speech input enabled."
            
        if mode in ["internet-search", "verify"]:
            result = self.search_online("4")
            self.mode = "chat"
            self.history.append({"role": "mikata", "content":result})
            with open("Resources\conversation_history.json", "w") as file:
                json.dump(self.history, file)

            return result, self.mode
        elif mode == "no-info":
            result = self.search_online("2")
            self.mode = "chat"
            self.history.append({"role": "mikata", "content":result})
            with open("Resources\conversation_history.json", "w") as file:
                json.dump(self.history, file)
            return result, self.mode
 
        try: 
            intent = self.intent_classifier_m.get_intent(query)

            if intent == "volume_up":                                     #Increase volume by 10
                volume_control.Increase()
                result = "Volume has been Increased."
            elif intent == "volume_down":                                 #Decrease Voplume by 10
                volume_control.Decrease()
                result = "Volume has been Decreased."
            elif intent == "volume_mute":                                 #Mute Volume , add-on - For music queries (precaution)
            
                if check_word_presence(query, ["pause", "pass"]):
                    result = "Song Paused."
                    self.audio_thread.pause_music()
                elif check_word_presence(query, ["stop"]):
                    result = "Song stopped."
                    self.audio_thread.stop_music()
                elif check_word_presence(query, ["resume", "continue"]):
                    result = "Song resumed."
                    self.audio_thread.resume_music()
                else:
                    volume_control.Min()
                    result = "The sound is muted"

            elif intent == "weather":                                     #For weather related queries     
                indices = {
                    "umbrellaIndex": ["umbrella", "rain"],
                    "walkingIndex": ["air quality", "outside", "walk"],
                    "dressingIndex": ["dress", "outfit", "wear"],
                    "heatIndex": ["heat", "hot", "hydrated"],
                    "uvIndex": ["uv", "uvrays", "protection"]
                }

                index = None

                day_n = weather.day_list()

                if "next" in query:
                    n = 7
                    day = None
                else:
                    n= 0
                    day = 1

                if day == None:
                    return "No data available for that day"

                for i in range(n, 10):
                    if day_n[i].lower() in query:
                        day = i+2
                        naal = day_n[i]
                        break            

                for idx, keywords in indices.items():
                    if any(keyword in query for keyword in keywords):
                        index = idx
                        break
                if index:
                    sum , des = weather.get_advice(index, day)
                    result = weather.set_advice(sum , des)
                    if day !=1:
                        result = result.replace("today", naal.lower())
                elif "days" in query:
                    print(int(query[query.find("day")-3:query.find("day")-1]))
                    result = weather.day_n_forcast(int(query[query.find("day")-3:query.find("day")-1]))
                else:
                    result = weather.weather(day)

            elif intent == "open":       #To open apps and websites
                app = replace_words(query, ["open ", "launch", "start", "can you", "please", "would you", "could you"])
                launch(app) 
                result = "Opening " + app

            elif intent == "close":                 #To close apps and websites (Should be Debugged)
                app = replace_words(query, ["stop", "close", "can you", "please", "would you", "could you"])
                close_app(app)
                result = "Closing " + app
            
            elif check_word_presence(query, ["search for", "look for", "loot it up", "search it"]):
                if "it" in query:
                    print("searching for previous query")
                    result = self.search_online("3")
                else:
                    print("Searching for current query")
                    #result = self.search_online("1")
                    result = web.google_search(replace_words(query, ["search for", "look for"]))
                
            elif intent == "music":                                        #To play and control music

                song_name = replace_words(query, ["pause", "pass", "resume", "continue", "stop", "play", "song", "music"])

                if mixer.music.get_busy():
                    if check_word_presence(query, ["pause", "pass"]):
                        result = "Song Paused."
                        self.audio_thread.pause_music()
                    elif check_word_presence(query, ["stop"]):
                        result = "Song stopped."
                        self.audio_thread.stop_music()
                    else:
                        result = "Song added to queue."
                        self.audio_thread = Audio(song_name)
                        self.audio_thread.start()                    

                else:
                    if check_word_presence(query, ["resume", "continue"]):
                        result = "Song resumed."
                        self.audio_thread.resume_music()
                    else:
                        result = "Song playing."
                        self.audio_thread = Audio(song_name)
                        self.audio_thread.start()
            
            else:
                query = replace_words(query, ["hi ", "hii "], "hello")
                result, self.sesID = convai_chat(query, self.sesID)

                self.history.append({"role": "mikata", "content":result})
                #print(self.history)

            no_info_phrases = data["incapable"]["no-information"]

            for phrase in no_info_phrases:
                if phrase in result:
                    print("Searching internet")
                    self.mode = "no-info"
                    with open("Resources\conversation_history.json", "w") as file:
                        json.dump(self.history, file)
                    return f"Mikata : Let me look that up for you. Please wait a moment", self.mode
                
            incapable_phrases = data["incapable"]["search-internet"]

            for phrase in incapable_phrases:
                if phrase in result:
                    print("Searching internet")
                    self.mode = "internet-search"
                    result = self.search_online("2")
                    self.mode = "chat"
                    
            with open("Resources\conversation_history.json", "w") as file:
                json.dump(self.history, file)
            
            self.mode = "chat"
            return f"Mikata : {result}", self.mode
        except Exception as e:
            print(e)
            return "An error occured", e

    def search_online(self, num):

        num = int(num)

        with open("Resources\conversation_history.json", "r") as history:
            hist = json.load(history)
            q = hist[-num]["content"]
            print(q)
        
        print(self.mode)

        try:
            result = web.wiki(q)
        except:
            result = web.google_search(q)

        return f"Mikata : {result}"
    
start_execution = Brain()

class GUI(QMainWindow): 
    finishSignal = pyqtSignal()

    def __init__(self):
        super(GUI, self).__init__()
        self.UI = Ui_MainWindow()
        self.UI.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.UI.snd_button.clicked.connect(self.get_command)

        self.UI.command.returnPressed.connect(self.get_command)

        self.scrollbar = self.UI.chatbox.verticalScrollBar()

        self.UI.play_button.clicked.connect(self.play_song)

        self.UI.pause_button.clicked.connect(self.pause_song)
        self.UI.pause_button.hide()

        self.UI.next_button.clicked.connect(self.next_song)

        start_execution.start()

        start_execution.updateSignal.connect(self.process_command)

        self.finishSignal.connect(start_execution.listen)

    def closeEvent(self, event):
        web.close_browser()
        event.accept()

    def next_song(self):
        try:
            start_execution.audio_thread.play_next()
        except:pass
    def pause_song(self):
        try:
            self.UI.pause_button.hide()
            self.UI.play_button.show()
            self.UI.play_button.raise_()
            start_execution.audio_thread.pause_music()
        except:pass

    def play_song(self):
        try:
            self.UI.play_button.hide()
            self.UI.pause_button.show()
            self.UI.pause_button.raise_()
            start_execution.audio_thread.resume_music()
        except:pass

    def get_command(self):
        if self.UI.command.text():
            self.query = self.UI.command.text()
            self.UI.command.clear()

            self.process_command()

    def process_command(self,query = None, mode = None):
        try:
            if self.speak_thread.is_alive():
                print("Wait till the response is finished.")
                return
        except:pass

        if query:
            self.query = query
        if mode:
            self.mode = mode

        self.UI.chatbox.appendPlainText(f"You : {self.query}")

        try: 
            self.response, self.mode = start_execution.get_response(self.query, self.mode)
        except:
            self.response, self.mode = start_execution.get_response(self.query, mode = "chat")

        print(self.response)
                    
        self.terminal_print(self.response)

        print(f"Mode is {self.mode}")

        if self.mode in ["internet-search", "verify"]:
            self.response = str(start_execution.search_online("4"))
            time.sleep(5)
            self.terminal_print(self.response)
        elif self.mode == "no-info":
            self.response, self.mode= start_execution.get_response("", mode="no-info")
            self.response = str(self.response)
            time.sleep(5)
            self.terminal_print(self.response)

        self.exit_statements = ["bye", "goodbye", "exit", "sayonara"]

        if self.query in self.exit_statements:
            ui.close()

    def terminal_print(self, text):
        # Add a newline character before the typewriting animation
        self.UI.chatbox.insertPlainText('\n')
        
        self.typewriting_text = text
        self.typewriting_index = 0

        # Set up a timer to call the update_typewriting function every 50 milliseconds
        self.typewriting_timer = QTimer(self)
        self.typewriting_timer.timeout.connect(self.update_typewriting)
        self.typewriting_timer.start(50)
        
        self.speak_thread = Thread(target=speak, args=(text.replace("Mikata :", ""),))
        self.speak_thread.start()


    def update_typewriting(self):
        # Append the next letter to the QPlainTextEdit
        if self.typewriting_index < len(self.typewriting_text):
            letter = self.typewriting_text[self.typewriting_index]
            self.UI.chatbox.insertPlainText(letter)
            self.typewriting_index += 1
            self.scrollbar.setValue(self.scrollbar.maximum())
        else:
            # Stop the timer when the typewriting is complete
            self.typewriting_timer.stop()
            self.speak_thread.join()
            self.finishSignal.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = GUI()
    ui.show()
    sys.exit(app.exec_())
