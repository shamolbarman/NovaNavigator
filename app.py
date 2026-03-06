import sys, threading, tkinter as tk, customtkinter as ctk, boto3, os, pygame, datetime, time, webbrowser, json
import speech_recognition as sr

# --- AWS CONFIGURATION (Security First: Using Environment Variables) ---
# Tip: On your local machine, set these as environment variables or use the defaults below for testing.
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', 'AKIAURBF27PON67Z35G3') 
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', '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')
REGION = 'us-east-1'

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY, 
    aws_secret_access_key=AWS_SECRET_KEY, 
    region_name=REGION
)

polly = session.client('polly')
bedrock = session.client('bedrock-runtime')

ctk.set_appearance_mode("dark")

class NovaNavigator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NovaNavigator AI - Agentic Web Robot")
        self.geometry("950x650")
        
        # Dashboard UI
        self.log = ctk.CTkTextbox(self, width=900, height=450, font=("Consolas", 14))
        self.log.pack(pady=20, padx=20)
        
        self.status_label = ctk.CTkLabel(self, text="Status: SYSTEM READY", font=("Arial", 14, "italic"), text_color="#00FF00")
        self.status_label.pack()

        self.btn = ctk.CTkButton(self, text="ACTIVATE NOVA AGENT", command=self.start_thread, 
                                 height=50, font=("Arial", 16, "bold"), fg_color="#FF9900")
        self.btn.pack(pady=10)

    def update_log(self, msg, tag="SYSTEM"):
        self.log.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{tag}] {msg}\n")
        self.log.see("end")

    def speak(self, text):
        """Amazon Polly Voice Synthesis"""
        self.update_log(text, "NOVA")
        fname = f"speech_{int(time.time())}.mp3"
        try:
            res = polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId='Joanna')
            with open(fname, "wb") as f: f.write(res['AudioStream'].read())
            pygame.mixer.init()
            pygame.mixer.music.load(fname)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): time.sleep(0.1)
            pygame.mixer.quit()
            if os.path.exists(fname): os.remove(fname)
        except Exception as e: self.update_log(f"Voice Error: {e}")

    def ask_nova_agent(self, prompt):
        """Amazon Nova Lite - Multi-step Reasoning"""
        try:
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": f"You are Nova, an AI agent for Shamol. Answer this briefly: {prompt}"}]
                    }
                ],
                "inferenceConfig": {"maxTokens": 300, "temperature": 0.5}
            })
            response = bedrock.invoke_model(modelId='amazon.nova-lite-v1:0', body=body)
            result = json.loads(response.get('body').read())
            return result['output']['message']['content'][0]['text']
        except Exception as e:
            return f"Agent Error: {str(e)}"

    def get_voice_cmd(self):
        """Speech Recognition Engine"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.status_label.configure(text="Status: LISTENING...", text_color="#FFD700")
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                return r.recognize_google(audio).lower()
            except: return None

    def hilv_verification(self, task):
        """Human-in-the-Loop Verification (HiLV) Security"""
        self.speak(f"Master Shamol, I am about to {task}. Do you give me permission? Say Yes or No.")
        answer = self.get_voice_cmd()
        if answer and "yes" in answer:
            self.speak("Permission granted. Executing task.")
            return True
        self.speak("Task declined for security.")
        return False

    def start_thread(self):
        threading.Thread(target=self.main_logic, daemon=True).start()

    def main_logic(self):
        self.speak("Hello Shamol. Nova Navigator is online. How can I assist you?")
        while True:
            cmd = self.get_voice_cmd()
            if not cmd: 
                self.status_label.configure(text="Status: IDLE", text_color="#00FF00")
                continue
            
            self.update_log(cmd, "SHAMOL")

            # Autonomous Web Actions
            if "search" in cmd:
                query = cmd.replace("search", "").strip()
                if self.hilv_verification(f"search Google for {query}"):
                    webbrowser.open(f"https://www.google.com/search?q={query}")
            
            elif "open youtube" in cmd:
                if self.hilv_verification("open YouTube"):
                    webbrowser.open("https://www.youtube.com")

            elif "shutdown" in cmd:
                if self.hilv_verification("shut down the PC"):
                    os.system("shutdown /s /t 10")

            elif "exit" in cmd or "stop" in cmd:
                self.speak("Going offline. Goodbye.")
                break
                
            else:
                self.status_label.configure(text="Status: THINKING...", text_color="#1E90FF")
                answer = self.ask_nova_agent(cmd)
                self.speak(answer)

if __name__ == "__main__":
    app = NovaNavigator()
    app.mainloop()
