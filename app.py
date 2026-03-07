import sys, threading, tkinter as tk, customtkinter as ctk, boto3, os, pygame, datetime, time, webbrowser, json
import speech_recognition as sr
import cv2
import pywhatkit
import google.generativeai as genai

# --- GEMINI CONFIGURATION ---
genai.configure(api_key="My_API_KEYS") 
model = genai.GenerativeModel('gemini-1.5-flash')

# --- AWS CONFIGURATION ---
AWS_ACCESS_KEY = 'MY_AWS_KEY' 
AWS_SECRET_KEY = 'MY_SECRET_KEY'
session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name='us-east-1')
polly = session.client('polly')

ctk.set_appearance_mode("dark")

class NovaRobot(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nova AI - Master Shamol Edition")
        self.geometry("1100x750")
        
        # Initialize Pygame Mixer for Audio
        pygame.mixer.init()
        
        # Dashboard UI
        self.log = ctk.CTkTextbox(self, width=1050, height=550, font=("Consolas", 14))
        self.log.pack(pady=20, padx=20)
        
        self.btn = ctk.CTkButton(self, text="ACTIVATE NOVA BRAIN", command=self.start_thread, 
                                 height=60, font=("Arial", 18, "bold"), fg_color="#27ae60")
        self.btn.pack(pady=10)

    def update_log(self, msg):
        """Standard logging for the dashboard"""
        self.log.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log.see("end")

    def speak(self, text):
        """Voice synthesis using Amazon Polly with Pygame playback"""
        self.update_log(f"Nova: {text}")
        # Unique filename to avoid file locking issues
        fname = f"speech_{int(time.time())}.mp3"
        try:
            res = polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId='Joanna')
            with open(fname, "wb") as f:
                f.write(res['AudioStream'].read())
            
            # Load and Play Audio
            pygame.mixer.music.load(fname)
            pygame.mixer.music.play()
            
            # Wait for audio to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Unload audio to unlock the file
            pygame.mixer.music.unload()
            
            # Delete temporary file
            if os.path.exists(fname):
                try: os.remove(fname)
                except: pass
                
        except Exception as e:
            self.update_log(f"Voice Error: {e}")

    def get_cmd(self):
        """Optimized Speech Recognition Engine"""
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
        """Run the main loop in a background thread to keep UI responsive"""
        threading.Thread(target=self.main_loop, daemon=True).start()

    def main_loop(self):
        """Core execution logic"""
        self.speak("Security Check Initiated.")
        
        # Simple Camera Confirmation
        cap = cv2.VideoCapture(0)
        ret, _ = cap.read()
        if ret:
            self.speak("Identity Confirmed. Welcome back, Master Shamol.")
        cap.release()
        
        while True:
            cmd = self.get_cmd()
            if not cmd:
                continue

            # 1. YouTube Player Action
            if "play" in cmd:
                song = cmd.replace("play", "").strip()
                self.speak(f"Playing {song} on YouTube.")
                pywhatkit.playonyt(song)

            # 2. Local System Control
            elif "open notepad" in cmd:
                self.speak("Opening Notepad.")
                os.system("notepad")

            # 3. AI Reasoning (Gemini Brain)
            elif any(x in cmd for x in ["hello", "tell me", "how", "what", "who", "why"]):
                self.speak("Thinking...")
                try:
                    prompt = f"You are Nova, an AI assistant for Master Shamol. Answer briefly in English: {cmd}"
                    response = model.generate_content(prompt)
                    answer = response.text.replace('*', '').strip()
                    self.speak(answer[:300]) 
                except Exception as e:
                    self.update_log(f"Brain Error: {e}")
                    self.speak("System Error: Neural connection lost.")

            # 4. Shutdown/Exit
            elif any(x in cmd for x in ["exit", "stop", "offline"]):
                self.speak("System going offline. Goodbye.")
                break
            
            # 5. Default Action: Web Search
            else:
                self.speak(f"Searching for {cmd}")
                webbrowser.open(f"https://www.google.com/search?q={cmd}")

if __name__ == "__main__":
    app = NovaRobot()
    app.mainloop()
