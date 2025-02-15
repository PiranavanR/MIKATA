# ✨Mikata v1

Mikata is a powerful AI assistant that can help you with a variety of tasks, from controlling your system's volume to searching the web and more.

## 🛠️Installation

### 1. Install Python  
Mikata requires **Python 3.x**.  

- 📥Download and install Python from [python.org](https://www.python.org/downloads/).
- ✅Verify installation with:

  ```
  python --version
  ```

### 2. Install Required Libraries
To use Mikata v1, you'll need to have the following dependencies installed:

- PyQt5
- TensorFlow
- Numpy
- Pandas
- Requests
- BeautifulSoup4
- Selenium
- Pytube
- Moviepy
- Pygame
- Pyttsx3
- Datefinder

📌You can install these dependencies using pip:

```
pip install -r requirements.txt
```
### 3. Download GloVe Embeddings  
Mikata uses pre-trained word embeddings for NLP tasks. You need to download the **GloVe 6B 100d** file and replace the existing one.  

#### 📌Steps:  
1. 📥Download the file from the official source:  [GloVe 6B 100d](https://nlp.stanford.edu/data/glove.6B.zip)  
2. 📂Extract the zip file.  
3. 🔍Locate **glove.6B.100d.txt** in the extracted folder.  
4. 🛠️Replace the existing `glove.6B.100d.txt` file in the project directory with the new one.  

✅Ensure the file path is correctly referenced in the code.  

### 4. Set Up ConvAI API 🧠
Mikata uses the **ConvAI API** for natural language processing. You need to set up an API key to enable its features.  

#### 📌Steps:  
1. **🌐Create an Account**  
   - Visit [ConvAI API](https://convai.com/) and sign up.  

2. **🔑Get Your API Key**  
   - After signing up, navigate to the **API section** in your ConvAI dashboard.  
   - Generate a new API key.  

3. **📝Configure the API Key in Mikata**  
   - Open the `Features.py` file in the project directory.  
   - Locate the `"CONVAI-API-KEY"` field on line 767.  
   - Replace the placeholder with your **ConvAI API key**:  

## 🚀Usage

To start using Mikata, simply run the `Brain.py` file:

```
python Brain.py
```

This will launch the Mikata GUI, where you can interact with the assistant by typing commands in the chat box.

Mikata supports the following commands:

- **✅Volume Control**: Use the commands "volume up", "volume down", and "volume mute" to control your system's volume.
- **✅Weather**: Ask Mikata about the weather, and it will provide you with information and recommendations based on the current conditions.
- **✅Web Search**: Use the command "search for [query]" to perform a Google search for the specified query.
- **✅Music**: Ask Mikata to play, pause, or stop music.
- **✅General Chat**: Mikata can engage in general conversation on a variety of topics.

## API

Mikata v1 uses Convai API for natural language processing tasks.


## 🤝Contributing

If you'd like to contribute to the Mikata project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

## 📜License

Mikata is licensed under the [MIT License](https://github.com/PiranavanR/MIKATA/blob/main/LICENSE)

## 🎯Conclusion  
Mikata is a versatile AI assistant designed to simplify everyday tasks, from voice commands to web automation. By following the setup instructions, installing dependencies, and configuring required APIs, you can unlock Mikata’s full potential.  
🔥 Whether you use it for productivity, entertainment, or automation, Mikata offers an intuitive and interactive experience.

💡 As the project evolves, your feedback & contributions are highly appreciated!

✨ Now that you're all set, go ahead and start using Mikata! 🚀

📩 We’d love to hear your thoughts!
