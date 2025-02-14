from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import requests
import datetime, json, random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from googlesearch import search
import threading
from pytube import YouTube
import os
import moviepy.editor as moviepy
from pygame import mixer
import wikipedia
import pyttsx3
import time
import re
import speech_recognition as sr
import datefinder
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences # type: ignore
import pickle
from datetime import timedelta, datetime
from datetime import date as datel

music_playlist = []
song_history = []

class Volume():
    def __init__(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

        # Get the current system volume
        self.current_volume = self.volume.GetMasterVolumeLevelScalar()

    def Increase(self):
        new_volume = min(1.0, self.current_volume + 0.1)
        self.volume.SetMasterVolumeLevelScalar(new_volume, None)
        self.current_volume = new_volume

    def Decrease(self):
        new_volume = max(0.0, self.current_volume - 0.1)
        self.volume.SetMasterVolumeLevelScalar(new_volume, None)
        self.current_volume = new_volume

    def Max(self):
        self.volume.SetMasterVolumeLevelScalar(1.0, None)
        self.current_volume = 1.0

    def Min(self):
        self.volume.SetMasterVolumeLevelScalar(0.0, None)
        self.current_volume = 0.0

    def SetVolume(self, to_volume):
        new_volume = min(1.0, to_volume / 100)
        new_volume = max(0.0, new_volume)
        self.volume.SetMasterVolumeLevelScalar(new_volume, None)
        self.current_volume = new_volume

class WebControl():
    def __init__(self) -> None:
        self.driver_path = r"Resources\\Drivers\\msedgedriver.exe"
        self.edge_service = Service(self.driver_path)
        # Initialize the Edge webdriver with the specified driver path
        options = EdgeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('detach', True)
        self.driver = webdriver.Edge(options=options, service=self.edge_service)
        #window_name = self.driver.execute_script("return window.name")
        #print(window_name)

    def check_open(self, url):
        tabs = self.driver.window_handles
        for tab in tabs:
            self.driver.switch_to.window(window_name=tab)
            print(self.driver.current_url)
            if url in self.driver.current_url:
                return True
        return False

    def launch_site(self, url):

        no_of_tabs =  len(self.driver.window_handles)

        if self.check_open(url):
            reopen = input("Site already open. Do you wanto to open the site in another tab again:")
            if "ye" in reopen:
                self.driver.execute_script(f"window.open('about:blank', '{no_of_tabs+1}tab');")
            
            # It is switching to second tab now
                self.driver.switch_to.window(f"{no_of_tabs+1}tab")
            
            # In the second tab, it opens geeksforgeeks
                self.driver.get(url)
            return
        else:
            #tabs =  self.driver.window_handles
            #print(tabs)
            if self.driver.title == "":
                self.driver.get(url)
            else:
                self.driver.execute_script(f"window.open('about:blank', '{no_of_tabs+1}tab');")
                
                # It is switching to second tab now
                self.driver.switch_to.window(f"{no_of_tabs+1}tab")
            
            # In the second tab, it opens geeksforgeeks
                self.driver.get(url)

    def close_site(self, url):
        if self.check_open(url):
            self.driver.close()
            return
        print("The site is not open!")

    def close_browser(self):
        self.driver.quit()

    def google_search(self, query):
        url = f"https://www.google.com/search?q={query}"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        search_results = soup.find_all("div", class_="BNeawe")
        answer = [result.text for result in search_results]

        return remove_words_after_last_punctuation(answer[0])

    def wiki(self, query):
        query = replace_words(query, ["what", "is", "define", "when did", "who", "do you know"])

        answer = wikipedia.summary(query, sentences = 2, auto_suggest=False)
        
        return answer

class Weather():

    def weather(self, day):
        #print(day)
        url = f"https://www.msn.com/en-us/weather/forecast/in-Tiruchirappalli,Tamil-Nadu?weadegreetype=C&day={day}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        current_temp = soup.find('div', id = "OverviewCurrentTemperature" ).text[:4]
        description = soup.find('div', id = "CurrentWeatherSummary").text
        if day == 1:
            return f"It's {current_temp}. {description}. {self.general_advice(day)}"
        else:
            return f"{description}. {self.general_advice(day)}"

    
    def day_list(self):

        week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ]
        dt = datetime.now()
        day = dt.strftime('%A')

        n = week_days.index(day)
        days_n = week_days[n+2:n+11]
        days_n.insert(0, "Tomorrow")

        return days_n

    def day_n_forcast(self, days = 10):

        #print(days)

        url = "https://www.msn.com/en-us/weather/forecast/in-Tiruchirappalli,Tamil-Nadu"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        high_n_day = []
        low_n_day = []
        weather_n_day = []

        high_temp = soup.find_all('div', class_ = "topTemp-E1_1 temp-E1_1")
        i = 0
        for high in high_temp:
            if i < days:
                high_t = int(high.text.replace("°", ""))
                high_t_c = temp_cvt(high_t, "F", "C")
                high_n_day.append(high_t_c)
                i = i + 1
            else:
                break
        high_avg = str(round(sum(high_n_day)/len(high_n_day)))
        high_one = int(high_avg[1])
        high_ten = int(high_avg) - int(high_one)

        low_temp = soup.find_all('div', class_ = "temp-E1_1")
        i = 0
        for low in low_temp:
            if i < days:
                try:
                    low_t = int(low.text.replace("°", ""))
                    low_t_c = temp_cvt(low_t, "F", "C")
                    low_n_day.append(low_t_c)
                except:
                    pass
            else:
                break
        low_avg = str(round(sum(low_n_day)/len(low_n_day)))
        low_one = int(low_avg[1])
        low_ten = int(low_avg) - int(low_one)

        weathers = soup.find_all('img', class_ = "iconTempPartIcon-E1_1")
        for wether in weathers:
            wthr = wether.get('title')
            if "Partly sunny" in wthr:
                wthr += "🌤"
            elif "Mostly sunny" in wthr:
                wthr += "☀️"
            elif "Sunny" in wthr:
                wthr += "☀️"
            elif "Haze" in wthr:
                wthr += "🌁"
            weather_n_day.append(wthr)
        #low_temp2 = soup.find_all('div', class_ = "temp-E1_1")
        #print(low_temp2) 

        days_n = self.day_list()
        
        low_high_high = "low"
        if high_one > 5:
            low_high_high = "high"
        low_high_low = "low"
        if low_one > 5:
            low_high_low = "high"

        nxt = "next" if days > 7 else ""

        result = f"From {days_n[0]} untill {nxt} {days_n[days-1]} high's will be in the {low_high_high} {high_ten}'s and low's will be in the {low_high_low} {low_ten}'s\n"
        
        same_weather = []
        c = True
        for i in range(10):
            if c == False:
                if i < days-1:
                    if weather_n_day[i] != weather_n_day[i+1]:
                        same_weather.append(i)
                        c = True
                elif i == days-1:
                    same_weather.append(i)

                continue
            if i < days-1:
                if weather_n_day[i] == weather_n_day[i+1]:
                    same_weather.append(i)
                    c = False

        i = 0

        while i <= days-1:
            if i in same_weather:
                j = same_weather.index(i)
                k = same_weather[j+1]
                and_until = "untill"
                from_on = "From"
                if (k - i) == 1:
                    and_until = "and"
                    from_on = "On"
                next_current = ""
                if i > 7:
                    next_current = " next"
                result = result + f"{from_on} {days_n[i]} {and_until} {next_current} {days_n[k]} it will be {weather_n_day[i]}."
                try:
                    i = k + 1
                except:
                    i = k
            else:
                result = result + f"On {days_n[i]} it will be {weather_n_day[i]}."
                i = i + 1
        return result
    
    def get_advice(self, index, day):

        url = f"https://www.msn.com/en-us/weather/life/in-Tiruchirappalli,Tamil-Nadu?lifeIndex={index}&day={day}"

        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        try:
            summary = soup.find('div', class_ = "wDailyTitleSection_summary-E1_1").text
        except:
            summary = soup.find('div', class_ = "wDailyTitleSection_summary-E1_1")

        if index != "walkingIndex":

            try:
                description = soup.find('div', class_ = "wDailyTipsSection_desc-E1_1").text
            except:
                description = None
        else:
            description = None

        return summary, description

    def assign_advice(self, summary):
        with open("Resources\Data.json") as f:
            data = json.load(f)
            advice = data['weather advice']
            if summary.lower() in advice:
                return advice[summary.lower()] 

    def set_advice(self, summary, description):
        full_summary = self.assign_advice(summary)
        if description != None:
            return random.choice([full_summary, description])
        else:
            return full_summary
        
    def general_advice(self, day):
        indices = ["umbrellaIndex", "heatIndex", "uvIndex"]
        req = ["must", "need", "likely needed", "extreme", "very high", "high", "extreme danger", "danger", "extreme caution"]
        for index in indices:
            sum , des = self.get_advice(index, day)
            if sum.lower() in req:
                adv = self.set_advice(sum, des)
                return adv
        ran = random.choice(["walkingIndex", "dressingIndex"])
        s, d =self.get_advice(ran, day)
        adv = self.set_advice(s,d)
        return adv

class Audio(threading.Thread):

    def __init__(self, song):
        super().__init__()
        self.song = song
        song_history.append(self.song)

    def run(self):
        if self.check_playing():
            self.add_queue(self.song)
            print("Song added to the queue")
            print(music_playlist)
        else:
            self.music_player(self.song)

    def yt_url_generator(self, song):

        song_query = song + " song youtube"

        search_results = search(song_query, num=1, stop=1, pause=2)

        first_result = next(search_results)

        return first_result

    def download_songs(self, song):
        yt = YouTube(self.yt_url_generator(song))
        song_name = yt.title

        song_name = replace_words(song_name, ['|', ","], "")

        isExist = os.path.isfile(f"D:\Project M.I.K.A.T.A\MIKATA 2.0\Resources\Temp\{song_name}.mp3")

        if isExist:
            exist =  True
        else:
            exist = False
            audio = yt.streams.filter(only_audio=True).last()
            print("Downloading song...")
            audio.download()
            print("Song downloaded.")
            song_name = song_name.replace("|", "")
            song_name = song_name.replace(",", "")
        print(song_name)
        return song_name, exist

    def music_player(self, song):

        self.paused = False

        song_name, exist = self.download_songs(song)

        if exist == False:
            self.audio_converter(song_name)

            os.rename(f"{song_name}.mp3", f"Resources\Temp\{song_name}.mp3")
            os.remove(f"{song_name}.webm")
        
        mixer.init()
        mixer.music.load(f"Resources\Temp\{song_name}.mp3")
        print(f"Playing {song}")
        mixer.music.play()
        while self.check_playing():
            time.sleep(1)
            pass

        print("song played successfully.")

        print(music_playlist)

        self.play_next()

    def pause_music(self):
        mixer.music.pause()
        self.paused = True

    def resume_music(self):
        mixer.music.unpause()
        self.paused = False

    def stop_music(self):
        mixer.music.stop()

    def audio_converter(self, song):
        clip = moviepy.AudioFileClip(f"{song}.webm")
        clip.write_audiofile(f"{song}.mp3")

    def check_playing(self):
        try:
            if mixer.music.get_busy():
                return True
            elif self.paused:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
        
    def add_queue(self, song):
        music_playlist.append(song)

    def play_next(self):
        if len(music_playlist) !=0:
            self.song = music_playlist[0]
            print("Next song from queue playing.")
            self.stop_music()
            music_playlist.remove(self.song) 
            print(music_playlist)
            self.music_player(song = self.song)

class IntentClassifier():
    def __init__(self,classes,model,tokenizer,label_encoder):
        self.classes = classes
        self.classifier = model
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder

    def get_intent(self,text):
        self.text = [text]
        self.test_keras = self.tokenizer.texts_to_sequences(self.text)
        self.test_keras_sequence = pad_sequences(self.test_keras, maxlen=16, padding='post')
        self.pred = self.classifier.predict(self.test_keras_sequence)
        return self.label_encoder.inverse_transform(np.argmax(self.pred,1))[0]

class Reminder():
    
    def get_params(self, text):
        
        text = text.lower()
        text = text.replace("remind me", "")
        text = text.replace("set a reminder", "")
        no_of_sentences = count_words(text, "and")
        sentences = []
        for i in range(0, no_of_sentences+1):
            if i == no_of_sentences:
                text = text.replace(" and ", "")
                sentences.append(text)
            else:
                index = text.find(" and")
                text1 = text[0:index]
                sentences.append(text1)
                text = text[index:]

        reminders = []

        for sentence in sentences:

            date_found = False
            is_today = False

            time = extract_time(sentence)
            if time:
                time = time[0].lower()
            elif "morning" in sentence:
                time = "9am"
            elif "afternoon" in sentence:
                time = "12pm"
            elif "evening" in sentence:
                time = "4pm"
            elif "night" in sentence:
                time = "7pm"
            elif "end of" in sentence:
                if "day" in sentence:
                    time = "8pm"
                elif "month" in sentence:
                    month = int(datetime.today().month)
                    year = int(datetime.today().year)
                    time = "9am"
                    if month == 12:
                        date = datetime(year, month, 31).strftime("%Y-%m-%d")
                    else:
                        date = (datetime(year, month + 1, 1) + timedelta(days=-1)).strftime("%Y-%m-%d")
                    date_found = True
                        
                elif "year" in sentence:
                    year = int(datetime.today().year)
                    date = datetime(year, 12, 31).strftime("%Y-%m-%d")
                    time = "9am"
                    date_found = True

            elif "beginning of" or "start of" in sentence:
                if "day" in sentence:
                    time = "8am"
                elif "month" in sentence:

                    month = int(datetime.today().month)
                    year = int(datetime.today().year)
                    time = "9am"
                    if datetime.today().day == 1:
                        is_today = True
                    else:
                        date = datetime(year, month+1, 1).strftime("%Y-%m-%d")
                    date_found = True
                        
                elif "year" in sentence:
                    year = int(datetime.today().year)
                    if datetime.today().day == 1 and datetime.today().month == 1:
                        is_today = True
                    else:
                        date = datetime(year+1, 1, 1).strftime("%Y-%m-%d")
                    time = "9am"
                    date_found = True
            elif "next" in sentence:
                if "month" in sentence:
                    month = int(datetime.today().month)
                    year = int(datetime.today().year)
                    time = "9am"
                    date = datetime(year, month+1, 1).strftime("%Y-%m-%d")
                elif "year" in sentence:
                    year = datetime.today().year
                    date = datetime(year+1, 1, 1).strftime("%Y-%m-%d") 
            else:
                time = "9am"
            
            sentence = sentence.replace(time, "")

            if not date_found:
                for day in self.day_dict():
                    if day.lower() in sentence:
                        date = self.day_dict()[day]
                        break
                    else:
                        date = self.day_dict()['Today']
                    
            time = self.convert_to_24_hour_format(time)

            repeat = False
            repeat_frequency = None
            time_interval = None

            if check_word_presence(sentence, ['every', 'daily', 'each']):
                repeat = True
                repeat_frequency, time_interval = self.extract_and_calculate_repetitive_reminder(sentence)
            
            task = replace_words(sentence, ["for ", "by ", "the ", "this ", "in ", "to ", "of ", "on ", "next ", "coming", "beginning", "end ", "every", "today", "daily ", "each ", "morning", "afternoon", "evening", "night", "tonight", "day", "week", "month", "year", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "at "])
            task =  re.sub(' +', ' ', task)

            reminders.append({
                "task" : task,
                "date" : date,
                "time" : time,
                "frequency" : repeat_frequency,
                "interval" : time_interval
            })

        # Find a reminder with a non-empty task
        non_empty_task_reminder = next((reminder for reminder in reminders if reminder['task'].strip()), None)

        # If a reminder with a non-empty task is found, assign its task to all reminders with an empty task
        if non_empty_task_reminder:
            for reminder in reminders:
                if not reminder['task'].strip():
                    reminder['task'] = non_empty_task_reminder['task']
        
        # Find a reminder with non-empty frequency and interval
        non_empty_freq_interval_reminder = next((reminder for reminder in reminders if reminder['frequency'] and reminder['interval']), None)

        # If a reminder with non-empty frequency and interval is found, assign them to the first reminder with empty values
        if non_empty_freq_interval_reminder:
            first_empty_freq_interval_reminder = next((reminder for reminder in reminders if not reminder['frequency'] and not reminder['interval']), None)
            if first_empty_freq_interval_reminder:
                first_empty_freq_interval_reminder['frequency'] = non_empty_freq_interval_reminder['frequency']
                first_empty_freq_interval_reminder['interval'] = non_empty_freq_interval_reminder['interval']

        return reminders

    def day_dict(self):
        days_list = []
        week_days = ["day", "week", "month" ,'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ]
        dt = datetime.now()
        day = dt.strftime('%A')

        n = week_days.index(day)
        days_n = week_days[n+2:n+11]
        days_n.insert(0, "Tomorrow")
        days_n.insert(0, "Today")
        for day in days_n:
            days_list.append((day, datel.today()+timedelta(days=days_n.index(day))))
        return dict(days_list)

    def extract_and_calculate_repetitive_reminder(self, text):
        # Define patterns for repetitive reminder extraction
        if check_word_presence(text, ['daily', 'everyday']):
            frequency = "day"
        else:
            pattern = r'(?:every|each)\s+(?P<frequency>day|week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?'
            match = re.search(pattern, text, re.IGNORECASE)
            frequency = match.group('frequency').lower() if match else None
        
        if frequency in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            frequency = "week"

        # Define time intervals for different frequencies
        intervals = {'day': timedelta(days=1),
                    'week': timedelta(weeks=1),
                    'month': timedelta(days=30),  # Assuming 30 days per month
                    'year': timedelta(days=365)}  # Assuming 365 days per year

        # Calculate time interval for the given frequency
        time_interval = intervals.get(frequency)

        print(time_interval, frequency)

        return frequency, time_interval

    def convert_to_24_hour_format(self, time_str):
        # Parse the time string to a datetime object
        try:
            time_obj = datetime.strptime(time_str, '%I%p')

            # Format the datetime object in 24-hour format
            time_24_hour_format = time_obj.strftime('%H:%M')
        except:
            time_obj = datetime.strptime(time_str, '%I:%M%p')

            # Format the datetime object in 24-hour format
            time_24_hour_format = time_obj.strftime('%H:%M')

        return time_24_hour_format

def extract_time(text):
    # Regular expression pattern to match time in various formats
    time_pattern = r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b|\b\d{1,2}\s*(?:AM|PM|am|pm)?\b'
    
    # Find all matches of the time pattern in the text
    matches = re.findall(time_pattern, text)
    
    # Return the list of matches
    return matches

def count_words(sentence, word):
    words = sentence.split()
    count =  0
    for w in words:
        if w == word:
            count += 1
    return count

def replace_words(query, words, replace_word = ""):
    for word in words:
        query = query.replace(word, replace_word)
    return query

def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    # Filter out non-numeric words
    numeric_words = [word for word in textnum.split() if word in numwords]

    current = result = 0
    for word in numeric_words:
        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

def temp_cvt(value, input, output):

    if input == "C":
        if output == "K":
            temp = value + 273.15
        elif output == "F":
            temp = value * (9/5) + 32
    elif input == "F":
        if output == "K":
            temp = (value - 32) * (5/9) + 273.15
        elif output == "C":
            temp = (value - 32) * (5/9)
    elif input == "K":
        if output == "F":
            temp = (value - 273.15) * (9/5) + 32
        elif output == "C":
            temp = value - 273.15
    return temp

def check_word_presence(string, word_list):
    for word in word_list:
        if word.lower() in string.lower():
            return True
    return False

def launch(app_name):
    try:
        from AppOpener import open
        open(app_name, match_closest = True, throw_error= True) # Opens whatsapp

    except:
        try:
            w = WebControl()
            search_results = search(app_name, num=1, stop=1, pause=2)
            first_result = next(search_results)
            print(f"Opening first search result for '{app_name}': {first_result}")
            w.launch_site(first_result)
        except Exception as e:
            print(f"An error occurred: {e}")

def close_app(app_name):
    try:
        from AppOpener import close
        close(app_name, match_closest = True, throw_error= True)
        print(app_name + " closed")

    except:
        try:
            w = WebControl()
            url = f"https://{app_name}.com"
            w.close_site(url)
        except:
            print(f"No app or site with the name {app_name}")

def convai_chat(query, sessionID):

    url = "https://api.convai.com/character/getResponse"

    payload = {
        'userText' : f'q{query}',
        'charID' : "44a04162-e466-11ee-87d5-42010a7be009",
    }

    headers = {
        'CONVAI-API-KEY' : "EnterYourAccessTokenHere"
    }

    response =  requests.request(method = "POST", url = url, headers = headers, data = payload)
    #print(response)
    data = response.json()
    #print(data)
    AI_response = data['text']
    sessionID = data['sessionID']

    return AI_response.replace("   ", ""), sessionID

def speak(query): 

    engine = pyttsx3.init()

    engine.setProperty('rate', 175)

    engine.setProperty('pitch', 2)   

    engine.say(query)
    
    engine.runAndWait()

def date_from_text(input):

    matches = list(datefinder.find_dates(input))
    if len(matches) > 0:
        # date returned will be a datetime.datetime object. here we are only using the first match.
        date = matches[0]
        print(date)
    else:
        print('No dates found')

def remove_words_after_last_punctuation(text):
    # Define a regular expression pattern to match the last punctuation mark
    pattern = r'[.,;:!?]\s*'
    
    # Find the index of the last punctuation mark in the text
    match = re.search(pattern, text[::-1])
    if match:
        last_punctuation_index = len(text) - match.end()
        
        # Remove words after the last punctuation mark
        text = text[:last_punctuation_index + 1]
    
    return text