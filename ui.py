import mysql.connector
import speech_recognition as sr
import time
import socket
import re
import tkinter as tk
from tk import *
import customtkinter
from cryptography.fernet import Fernet
from parrot import Parrot
import torch
import warnings
warnings.filterwarnings("ignore")
from playsound import playsound
from googletrans import Translator
from gtts import gTTS
import os
flag = 0
from tkinter.filedialog import askopenfilename,asksaveasfilename
from PIL import Image, ImageTk


global dests
global dests2

def transcribe_audio_from_microphone():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Say something!")
        audio = recognizer.listen(source, timeout=10.0)
    try:
        transcription = recognizer.recognize_google(audio)
        print("You said: " + transcription)
    except sr.UnknownValueError:
        transcription = "Could not transcribe audio"
        print(transcription)
    return transcription

def transcribe_audio_from_microphone_nepali():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Say something!")
        audio = recognizer.listen(source, timeout=10.0)
        transcription = recognizer.recognize_google(audio,language='ne')
        print("You said: " + transcription)
    # except sr.UnknownValueError:
    #     transcription = "Could not transcribe audio"
    #     print(transcription)
    return transcription

def encrypt_data(plaintext):
    # Generate a key and encrypt the data
    key = Fernet.generate_key()
    cipher = Fernet(key)
    ciphertext = cipher.encrypt(plaintext.encode("utf-8"))
    return (key, ciphertext)

def log_transcription(transcription):
    global logs_inserted
    if logs_inserted:
        # transcription has already been logged
        return
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="hello"
    )
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INT AUTO_INCREMENT PRIMARY KEY, log_time INTEGER, transcription TEXT, ip_address BLOB, encryption_key BLOB)")
    
    # Create datas table if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS datas (id INT AUTO_INCREMENT PRIMARY KEY, text TEXT)")
    
    # Write transcription to a text file
    with open("transcription.txt", "a") as f:
        f.write(transcription + "\n")
    
    # Insert transcription into datas table
    cursor.execute("INSERT INTO datas (text) VALUES (%s)", (transcription,))
    

    # Check if transcription contains any profanity
    with open("badwords.txt") as f:
        bad_words = f.read().splitlines()
        
    for word in bad_words:
        if re.search(r"\b" + word.lower() + r"\b", transcription, re.IGNORECASE):
            transcription = "Sorry, profanity is not allowed."
            break
    
    ip_address = socket.gethostbyname(socket.gethostname())
    encryption_key, encrypted_ip_address = encrypt_data(ip_address)
    
    cursor.execute("INSERT INTO logs (log_time, transcription, ip_address, encryption_key) VALUES (%s, %s, %s, %s)", (int(time.time()), transcription, encrypted_ip_address, encryption_key))
    connection.commit()
    cursor.close()
    connection.close()
    logs_inserted = True

def start_button_clicked():
    global transcription

    # transcription_label=event.transcription_label
    # selection_start, selection_end = widget.tag_ranges("sel")
    transcription = transcribe_audio_from_microphone()
    # aa.config(text= transcription)
    # aa.tag_remove("start",  "1.0", 'end')
    aa.delete(1.0,tk.END)
    aa.insert(tk.INSERT,transcription)
    # transcription_label.tag_configure("highlight", background="yellow")
    # transcription_label.tag_add("highlight", selection_start, selection_end)
    # end_button.config(state=tk.NORMAL)   #refresh

def start_button_clicked_Nepali():
    global transcription
    # transcription_label=event.transcription_label
    # selection_start, selection_end = widget.tag_ranges("sel")
    transcription = transcribe_audio_from_microphone_nepali()
    # transcription_label.config(text= transcription)
    aa.delete(1.0,tk.END)
    aa.insert(tk.INSERT,transcription)
    # transcription_label.tag_configure("highlight", background="yellow")
    # transcription_label.tag_add("highlight", selection_start, selection_end)
    # end_button.config(state=tk.NORMAL)   #refresh    

def end_button_clicked():
    global transcription, logs_inserted
    if transcription is None:
        # transcription has not been recorded yet
        return
    log_transcription(transcription)
    transcription = None
    logs_inserted = False
    end_button.config(state=tk.DISABLED)

def ended():
    root.destroy()    

def highlight_text(event, color):
    widget = event.widget
    try:
        selection_start, selection_end = widget.tag_ranges("sel")
    except:
        return
    widget.tag_configure("highlight", background=color)
    widget.tag_add("highlight", selection_start, selection_end)  


def high():
    # widget = event.widget
    # selection_start, selection_end = widget.tag_ranges("sel")
    # text.tag_add("start", selection_start, selection_end)
    aa.tag_add("start", "sel.first","sel.last")
    aa.tag_config("start", background= "black", foreground= "white")      

def vevo():
    parrot=Parrot(model_tag="prithivida/parrot_paraphraser_on_T5",use_gpu=False)

    phrases=[transcription]

    for phrase in phrases:
        print("-"*100)
        print("Input_phrase:",phrase)
        print("-"*100)
        para_phrases=parrot.augment(input_phrase=phrase)
        for para_phrase in para_phrases:
            aa.delete(1.0,tk.END)
            aa.insert(tk.INSERT,para_phrase)
            print(para_phrase)


def open_nep():
    file = askopenfilename(defaultextension=".txt",
                                  filetypes=[("All Files","*.*"),
                                    ("Text Documents","*.txt")])


    with open(file,'r', encoding='utf-16') as f:
        aa.delete(1.0,tk.END)
        aa.insert(tk.INSERT,f.read())


def openFile():
         
    file = askopenfilename(defaultextension=".txt",
                                      filetypes=[("All Files","*.*"),
                                        ("Text Documents","*.txt")])
  
            # Try to open the file
            # set the window title
    root.title(os.path.basename(file) + " - WhiteBoard")
    # thisTextArea.delete(1.0,END)
 
    file = open(file,"r")
 
    # thisTextArea.insert(1.0,file.read())
    aa.delete(1.0,tk.END)
    aa.insert(tk.INSERT,file.read())
 
    file.close()

def clear():
    aa.delete(1.0,tk.END)

def saveFileNep():
 
    file = asksaveasfilename(initialfile='Untitled.txt',
                                            defaultextension=".txt",
                                            filetypes=[("All Files","*.*"),
                                                ("Text Documents","*.txt")])
 
                # Try to save the file
    file = open(file,"w",encoding='utf-16')
    file.write(transcription)
    file.close()

def saveFile():
 
    file = asksaveasfilename(initialfile='Untitled.txt',
                                            defaultextension=".txt",
                                            filetypes=[("All Files","*.*"),
                                                ("Text Documents","*.txt")])
 
                # Try to save the file
    file = open(file,"w")
    file.write(transcription)
    file.close()    
                 
                # Change the window title
    # root.title(os.path.basename(file) + " - Notepad")
                 
             
    #     else:
    #         file = open(file,"w")
    #         file.write(thisTextArea.get(1.0,END))
    #         file.close()                        

def saveFile_trans():
 
    file = asksaveasfilename(initialfile='Untitled.txt',
                                            defaultextension=".txt",
                                            filetypes=[("All Files","*.*"),
                                                ("Text Documents","*.txt")])
 
                # Try to save the file
    file = open(file,"w")
    file.write(text_to_translate.text)
    file.close()

def trans():


    global text_to_translate
    translator = Translator()
    text_to_translate = translator.translate(transcription, dest='en')
    # transcription_label.config(text= text_to_translate.text)
    aa.delete(1.0,tk.END)
    aa.insert(tk.INSERT,text_to_translate.text)


    text = text_to_translate.text
    print(text)

    # voice=gTTS(text_to_translate,lang=dests)
    # voice.save("voice.mp3")
    # playsound("voice.mp3")

def voice_trans():
    voice=gTTS(text_to_translate.text,lang='en')
    voice.save("voice.mp3")
    playsound("voice.mp3")
    os.remove("voice.mp3")    

root = tk.Tk()
root.geometry("900x900")
root.title("White Board")


photo=Image.open("on.png")
resize=photo.resize((27,27))
light = ImageTk.PhotoImage(resize)
pho=Image.open("off.png")
resizes=pho.resize((27,27))
dark=ImageTk.PhotoImage(resizes)


switch_value = True

# Defining a function to toggle
# between light and dark theme
def toggle():

    global switch_value
    if switch_value == True:
        switch.config(image=dark, bg="#26242f",
                    activebackground="#26242f")
        
        # Changes the window to dark theme
        root.config(bg="#26242f")
        switch_value = False

    else:
        switch.config(image=light, bg="white",
                    activebackground="white")
        
        # Changes the window to light theme
        root.config(bg="white")
        switch_value = True


# Creating a button to toggle
# between light and dark themes
switch = tk.Button(root, image=light,
                bd=0, bg="white",
                activebackground="white",
                command=toggle)
switch.pack(padx=50, pady=150)
switch.place(x=25, y=600)  # Set the position using .place()



dic = ('afrikaans', 'af', 'albanian', 'sq',
    'amharic', 'am', 'arabic', 'ar',
    'armenian', 'hy', 'azerbaijani', 'az',
    'basque', 'eu', 'belarusian', 'be',
    'bengali', 'bn', 'bosnian', 'bs', 'bulgarian',
    'bg', 'catalan', 'ca', 'cebuano',
    'ceb', 'chichewa', 'ny', 'chinese (simplified)',
    'zh-cn', 'chinese (traditional)',
    'zh-tw', 'corsican', 'co', 'croatian', 'hr',
    'czech', 'cs', 'danish', 'da', 'dutch',
    'nl', 'english', 'en', 'esperanto', 'eo',
    'estonian', 'et', 'filipino', 'tl', 'finnish',
    'fi', 'french', 'fr', 'frisian', 'fy', 'galician',
    'gl', 'georgian', 'ka', 'german',
    'de', 'greek', 'el', 'gujarati', 'gu',
    'haitian creole', 'ht', 'hausa', 'ha',
    'hawaiian', 'haw', 'hebrew', 'he', 'hindi',
    'hi', 'hmong', 'hmn', 'hungarian',
    'hu', 'icelandic', 'is', 'igbo', 'ig', 'indonesian',
    'id', 'irish', 'ga', 'italian',
    'it', 'japanese', 'ja', 'javanese', 'jw',
    'kannada', 'kn', 'kazakh', 'kk', 'khmer',
    'km', 'korean', 'ko', 'kurdish (kurmanji)',
    'ku', 'kyrgyz', 'ky', 'lao', 'lo',
    'latin', 'la', 'latvian', 'lv', 'lithuanian',
    'lt', 'luxembourgish', 'lb',
    'macedonian', 'mk', 'malagasy', 'mg', 'malay',
    'ms', 'malayalam', 'ml', 'maltese',
    'mt', 'maori', 'mi', 'marathi', 'mr', 'mongolian',
    'mn', 'myanmar (burmese)', 'my',
    'nepali', 'ne', 'norwegian', 'no', 'odia', 'or',
    'pashto', 'ps', 'persian', 'fa',
    'polish', 'pl', 'portuguese', 'pt', 'punjabi',
    'pa', 'romanian', 'ro', 'russian',
    'ru', 'samoan', 'sm', 'scots gaelic', 'gd',
    'serbian', 'sr', 'sesotho', 'st',
    'shona', 'sn', 'sindhi', 'sd', 'sinhala', 'si',
    'slovak', 'sk', 'slovenian', 'sl',
    'somali', 'so', 'spanish', 'es', 'sundanese',
    'su', 'swahili', 'sw', 'swedish',
    'sv', 'tajik', 'tg', 'tamil', 'ta', 'telugu',
    'te', 'thai', 'th', 'turkish',
    'tr', 'ukrainian', 'uk', 'urdu', 'ur', 'uyghur',
    'ug', 'uzbek', 'uz',
    'vietnamese', 'vi', 'welsh', 'cy', 'xhosa', 'xh',
    'yiddish', 'yi', 'yoruba',
    'yo', 'zulu', 'zu')

# canvas= tk.Canvas(root, width= 10, height=20, bg="SpringGreen2")

# #Add a text in Canvas
# canvas.create_text(300, 50, text="HELLO WORLD", fill="black", font=('Helvetica 15 bold'))
# canvas.pack()
dic2 = ('afrikaans', 'af', 'albanian', 'sq',
    'amharic', 'am', 'arabic', 'ar',
    'armenian', 'hy', 'azerbaijani', 'az',
    'basque', 'eu', 'belarusian', 'be',
    'bengali', 'bn', 'bosnian', 'bs', 'bulgarian',
    'bg', 'catalan', 'ca', 'cebuano',
    'ceb', 'chichewa', 'ny', 'chinese (simplified)',
    'zh-cn', 'chinese (traditional)',
    'zh-tw', 'corsican', 'co', 'croatian', 'hr',
    'czech', 'cs', 'danish', 'da', 'dutch',
    'nl', 'english', 'en', 'esperanto', 'eo',
    'estonian', 'et', 'filipino', 'tl', 'finnish',
    'fi', 'french', 'fr', 'frisian', 'fy', 'galician',
    'gl', 'georgian', 'ka', 'german',
    'de', 'greek', 'el', 'gujarati', 'gu',
    'haitian creole', 'ht', 'hausa', 'ha',
    'hawaiian', 'haw', 'hebrew', 'he', 'hindi',
    'hi', 'hmong', 'hmn', 'hungarian',
    'hu', 'icelandic', 'is', 'igbo', 'ig', 'indonesian',
    'id', 'irish', 'ga', 'italian',
    'it', 'japanese', 'ja', 'javanese', 'jw',
    'kannada', 'kn', 'kazakh', 'kk', 'khmer',
    'km', 'korean', 'ko', 'kurdish (kurmanji)',
    'ku', 'kyrgyz', 'ky', 'lao', 'lo',
    'latin', 'la', 'latvian', 'lv', 'lithuanian',
    'lt', 'luxembourgish', 'lb',
    'macedonian', 'mk', 'malagasy', 'mg', 'malay',
    'ms', 'malayalam', 'ml', 'maltese',
    'mt', 'maori', 'mi', 'marathi', 'mr', 'mongolian',
    'mn', 'myanmar (burmese)', 'my',
    'nepali', 'ne', 'norwegian', 'no', 'odia', 'or',
    'pashto', 'ps', 'persian', 'fa',
    'polish', 'pl', 'portuguese', 'pt', 'punjabi',
    'pa', 'romanian', 'ro', 'russian',
    'ru', 'samoan', 'sm', 'scots gaelic', 'gd',
    'serbian', 'sr', 'sesotho', 'st',
    'shona', 'sn', 'sindhi', 'sd', 'sinhala', 'si',
    'slovak', 'sk', 'slovenian', 'sl',
    'somali', 'so', 'spanish', 'es', 'sundanese',
    'su', 'swahili', 'sw', 'swedish',
    'sv', 'tajik', 'tg', 'tamil', 'ta', 'telugu',
    'te', 'thai', 'th', 'turkish',
    'tr', 'ukrainian', 'uk', 'urdu', 'ur', 'uyghur',
    'ug', 'uzbek', 'uz',
    'vietnamese', 'vi', 'welsh', 'cy', 'xhosa', 'xh',
    'yiddish', 'yi', 'yoruba',
    'yo', 'zulu', 'zu')



# variable = tk.StringVar(root)
# # variable.set('ne') # default value

# w = tk.OptionMenu(root, variable,"ne","hi","Ja")
# w.pack()

# dests=variable.get()

# variable2 = tk.StringVar(root)
# # variable2.set('ne')

# w2 = tk.OptionMenu(root, variable2,"ne","hi","Ja")
# w2.pack()

# dests2=variable2.get()

text= tk.Text(root);

#Create a Button to highlight text

aa= tk.Text(root,width=140, height=42);



transcription = ""
logs_inserted = False

# transcription_label = tk.Label(root, text="")
# transcription_label = tk.Label(root, text="")       #edited
# transcription_label.pack()
# transcription_label.bind("<Button-1>", lambda event: highlight_text(event, "yellow"))

start_button = customtkinter.CTkButton(root, text="English", command=start_button_clicked, fg_color='#72747a', hover_color='#9d9c9a')
start_button.place(x=25, y=35)


start_button = customtkinter.CTkButton(root, text="Nepali", command=start_button_clicked_Nepali, fg_color='#72747a', hover_color='#9d9c9a')
start_button.place(x=25, y=70)

end_button = customtkinter.CTkButton(root, text="End", command=ended, fg_color='#72747a', hover_color='#9d9c9a')
end_button.place(x=25, y=420)

para_button = customtkinter.CTkButton(root, text="Paraphrase", command=vevo, fg_color='#72747a', hover_color='#9d9c9a')
para_button.place(x=25, y=140)

trans_button = customtkinter.CTkButton(root, text="Translate to English", command=trans, fg_color='#72747a', hover_color='#9d9c9a')
trans_button.place(x=25, y=175)

open_button = customtkinter.CTkButton(root, text="Open English", command=openFile, fg_color='#72747a', hover_color='#9d9c9a')
open_button.place(x=25, y=210)

open_nepp = customtkinter.CTkButton(root, text="Open Nepali", command=open_nep, fg_color='#72747a', hover_color='#9d9c9a')
open_nepp.place(x=25, y=245)

save_button = customtkinter.CTkButton(root, text="Save English", command=saveFile, fg_color='#72747a', hover_color='#9d9c9a')
save_button.place(x=25, y=350)

save_button = customtkinter.CTkButton(root, text="Save  Nepali", command=saveFileNep, fg_color='#72747a', hover_color='#9d9c9a')
save_button.place(x=25, y=315)

save_button_trans = customtkinter.CTkButton(root, text="Save Translation", command=saveFile_trans, fg_color='#72747a', hover_color='#9d9c9a')
save_button_trans.place(x=25, y=280)

speech_button_trans = customtkinter.CTkButton(root, text="Translation speech", command=voice_trans, fg_color='#72747a', hover_color='#9d9c9a')
speech_button_trans.place(x=25, y=105)
hlt=customtkinter.CTkButton(root, text= "Highlight", command=high, fg_color='#72747a', hover_color='#9d9c9a')
hlt.place()

clear=customtkinter.CTkButton(root, text= "Clear", command=clear, fg_color='#B20000', hover_color='#FDB10B')
clear.place(x=25,y=0)

hlt=customtkinter.CTkButton(root, text= "Highlight", command=high, fg_color='#72747a', hover_color='#9d9c9a')
hlt.place(x=25,y=385)

aa.place(x=185, y=0)
aa.insert(tk.INSERT,str(transcription))
text.place(x=185, y=0)

# hlt=tk.Button(root, text= "Highlight", command= high)
# hlt.pack()
# widget = tk.Text(root, cursor="dotbox")
# widget.pack()
# widget.bind("<Button-1>", lambda event: highlight_text(event, "yellow"))
# highlibtn=tk.Button(root, text= "Highlight", command= add_highlighter)
# highlibtn.pack()


root.mainloop()






#paraphrase done
#s2t done
#paraphrase dictionary done
#highlight after db retrieval done
#database retrieval done
#record can be done later
#translation remaining a bit for audio
#noise reduction
#real time