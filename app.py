import sys, threading, tkinter as tk, customtkinter as ctk, boto3, os, pygame, datetime, time, webbrowser, json
import speech_recognition as sr
import cv2
import pywhatkit

# --- AWS & NOVA 
AWS_ACCESS_KEY = 'My_AWS_ACCESS_KEY' 
AWS_SECRET_KEY = 'My_AWS_SECRET_KEY'
REGION = 'us-east-1'

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY, 
    aws_secret_access_key=AWS_SECRET_KEY, 
    region_name=REGION
)

bedrock = session.client(service_name='bedrock-runtime')
polly = session.client('polly')

ctk.set_appearance_mode("dark")

class NovaRobot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nova AI - Master Shamol Edition")
        self.geometry("1100x750")
        pygame.mixer.init()
        
        self.log = ctk.CTkTextbox(self, width=1050, height=550, font=("Consolas", 14))
        self.log.pack(pady=20, padx=20)
        
        self.btn = ctk.CTkButton(self, text="ACTIVATE NOVA BRAIN", command=self.start_thread, 
                                 height=60, font=("Arial", 18, "bold"), fg_color="#27ae60")
        self.btn.pack(pady=10)

    def update_log(self, msg):
        self.log.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log.see("end")

    def speak(self, text):
        self.update_log(f"Nova: {text}")
        fname = f"speech_{int(time.time())}.mp3"
        try:
            res = polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId='Joanna')
            with open(fname, "wb") as f:
                f.write(res['AudioStream'].read())
            
            pygame.mixer.music.load(fname)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.music.unload()
            if os.path.exists(fname):
                try: os.remove(fname)
                except: pass
        except Exception as e:
            self.update_log(f"Voice Error: {e}")

    def get_cmd(self):
        r = sr.Recognizer()
        r.energy_threshold = 400 
        r.dynamic_energy_threshold = True
        with sr.Microphone() as source:
            self.update_log("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.8) 
            try:
                audio = r.listen(source, timeout=7, phrase_time_limit=10)
                cmd = r.recognize_google(audio, language='en-IN').lower()
                self.update_log(f"User: {cmd}")
                return cmd
            except:
                return None

    def start_thread(self):
        threading.Thread(target=self.main_loop, daemon=True).start()

    def main_loop(self):
        self.speak("Security Check Initiated.")
        cap = cv2.VideoCapture(0)
        ret, _ = cap.read()
        if ret:
            self.speak("Identity Confirmed. Welcome back, Master Shamol.")
        cap.release()
        
        while True:
            cmd = self.get_cmd()
            if not cmd:
                continue

            if "play" in cmd:
                song = cmd.replace("play", "").strip()
                self.speak(f"Playing {song} on YouTube.")
                pywhatkit.playonyt(song)

            elif "open notepad" in cmd:
                self.speak("Opening Notepad.")
                os.system("notepad")

            elif any(x in cmd for x in ["hello", "tell me", "how", "what", "who", "why", "nova"]):
                self.speak("Thinking with Amazon Nova...")
                try:
                    native_request = {
                        "messages": [
                            {
                                "role": "user",
                                "content": [{"text": f"You are Nova, a helpful AI assistant for Master Shamol. Briefly answer: {cmd}"}]
                            }
                        ],
                        "inferenceConfig": {"maxNewTokens": 300, "temperature": 0.7}
                    }
                    response = bedrock.invoke_model(
                        modelId="us.amazon.nova-lite-v1:0", 
                        body=json.dumps(native_request)
                    )
                    model_response = json.loads(response["body"].read())
                    answer = model_response["output"]["message"]["content"][0]["text"]
                    self.speak(answer.replace('*', '').strip())
                except Exception as e:
                    self.update_log(f"Nova Error: {e}")
                    self.speak("I am having trouble connecting to AWS Bedrock.")

            elif any(x in cmd for x in ["exit", "stop", "offline"]):
                self.speak("System going offline. Goodbye.")
                break
            
            else:
                self.speak(f"Searching for {cmd}")
                webbrowser.open(f"https://www.google.com/search?q={cmd}")

if __name__ == "__main__":
    app = NovaRobot()
    app.mainloop()
