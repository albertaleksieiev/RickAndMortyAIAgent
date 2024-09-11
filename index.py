import os
import json
from datetime import datetime
import anthropic
from openai import OpenAI
import subprocess
import fakeyou
from time import sleep
import requests
from playsound import playsound
import threading
import concurrent.futures  # Add this import
from DatabaseHandler import DatabaseHandler
from MemoryManager import MemoryManager
from ReflectionAgent import ReflectionAgent
from FriendAgent import FriendAgent

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize clients
openAIClient = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize FakeYou client only if credentials are available
fakeyou_email = os.getenv('FAKEYOU_EMAIL')
fakeyou_password = os.getenv('FAKEYOU_PASSWORD')
fake_you_client = None
if fakeyou_email and fakeyou_password:
    fake_you_client = fakeyou.FakeYou(False)
    fake_you_client.login(fakeyou_email, fakeyou_password)

# Initialize the Anthropic client
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

client = anthropic.Anthropic(api_key=api_key)

def play_background_music(filename, stop_event):
    while not stop_event.is_set():
        playsound(filename)

def infinite_chat():
    memory_manager = MemoryManager()
    reflection_agent = ReflectionAgent(memory_manager, client)
    friend_agent = FriendAgent(memory_manager, client)

    while True:
        user_input = input("👤 You: ")
        if user_input.lower() == 'exit':
            break
        
        response = friend_agent.respond(user_input)
        print("🤖 AI: " + response)

    # Perform reflection on the conversation thread at the end of the conversation
    reflection_result = reflection_agent.reflect_on_thread()
    print("🧐 Final Reflection:")
    print(json.dumps(reflection_result, indent=2))
    memory_manager.add_conversation_summary(reflection_agent.summarize_conversation())

def save_image(image_url, file_name):
    import requests
    """Download an image from the given URL and save it locally."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Image saved successfully as {file_name}")
        return file_name
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        return None
    
def generate_image(prompt):
    """Generate an image using DALL-E based on the given prompt."""
    try:
        response = openAIClient.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return save_image(image_url, 'image.jpg')
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def display_image(image_path):
    """Display the image using catimg."""
    try:
        subprocess.run(['catimg', image_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error displaying image: {e}")

def generate_and_save_audio(text, voice_model_token="weight_0f762jdzgsy1dhpb86qxy4ssm", output_filename="voice.wav", max_rounds=20):
    # Start TTS job
    job_token = fake_you_client.make_tts_job(text, voice_model_token)

    rounds = 0
    while True:
        if rounds > max_rounds:
            print("Max rounds reached. Job timed out.")
            return None

        job_status = fake_you_client.tts_status(job_token)
        #print(f"Job status: {job_status}")

        if job_status == "complete_success":
            # Job is complete, retrieve the synthesized audio
            synthesized_audio = fake_you_client.tts_poll(job_token)
            audio_url = str(synthesized_audio.link)

            # Download and save the audio file
            response = requests.get(audio_url)
            if response.status_code == 200:
                with open(output_filename, 'wb') as file:
                    file.write(response.content)
                #print(f"Audio saved as {output_filename}")
                return output_filename
            else:
                print("Failed to download the audio file.")
                return None

        elif job_status in ["dead", "attempt_failed"]:
            print("Job failed.")
            return None

        else:
            #print(f"Waiting... (Round {rounds + 1})")
            sleep(3)

        rounds += 1

def enhanced_infinite_chat():
    print("-" * 50)
    print("""
                                                               
                            33                             
                            007                            
              7            0118                            
              0485        03118                            
              78113047  70111154       3007                
               631111106421111103  1403160                 
               701111111111111130021111388                 
                 0111113837777302111111507                 
                 431181777777777778311190                  
        8831111111110777729542774091211027                 
          39511111167771417835491247741325560000           
            70311112969236423777777392311148007            
              283112777777737777447644911804               
               401142777317467       272114005             
          500211111625  7   2751    677811138804           
            4023111376     2777177779676559006             
                4011877777761770733177703459               
                 9130371177774797777777009180              
               9611371777777777777777160980009             
             76680065917777743312177730009                 
                   21121023771573777728000                 
                   85600717778253937200                    
                       504777777771808                     
                          1061113005                       
                          10077777909                      
    """)
    print("💾 Type '/exit' to end the conversation and save data. Otherwise, all data will be lost.")
    print("🔊 Type '/mute' to toggle background music on/off.")
    print("-" * 50)
    
    memory_manager = MemoryManager()
    friend_agent = FriendAgent(memory_manager, client)
    reflection_agent = ReflectionAgent(memory_manager, client)
    
    muted = False
    background_music_thread = None
    stop_music_event = threading.Event()

    while True:
        if not muted and background_music_thread is None:
            # Start playing background music
            stop_music_event.clear()
            background_music_thread = threading.Thread(target=play_background_music, args=("./resources/audio_waiting.mp3", stop_music_event))
            background_music_thread.start()

        user_input = input("👤 You: ")
        if user_input.lower() == '/exit':
            print("💾 Saving data and ending conversation...")
            break
        elif user_input.lower() == '/mute':
            muted = not muted
            if muted:
                print("🔇 Background music muted.")
                if background_music_thread:
                    stop_music_event.set()
                    background_music_thread.join()
                    background_music_thread = None
            else:
                print("🔊 Background music unmuted.")
            continue

        response = friend_agent.respond(user_input)

        # Use ThreadPoolExecutor for better thread management
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            image_future = executor.submit(generate_image, reflection_agent.reflect_for_image_generation())
            
            # Only generate audio if FakeYou client is available
            if fake_you_client:
                audio_future = executor.submit(generate_and_save_audio, response)
            else:
                audio_future = None

        # Wait for both futures to complete
        image_path = image_future.result()
        audio_path = audio_future.result() if audio_future else None

        # Stop background music before playing AI response audio
        if background_music_thread:
            stop_music_event.set()
            background_music_thread.join()
            background_music_thread = None
        # Display image and play audio when both are ready
        if image_path:
            display_image(image_path)
        print("🤖 AI: " + response)
        if audio_path:
            playsound(audio_path)
    

    # Perform reflection on the conversation thread at the end of the conversation
    reflection_result = reflection_agent.reflect_on_thread()
    print("🧐 Final Reflection:")
    print(json.dumps(reflection_result, indent=2))
    memory_manager.add_conversation_summary(reflection_agent.summarize_conversation())

def generate_and_display_image(reflection_agent):
    image_path = generate_image(reflection_agent.reflect_for_image_generation())
    if image_path:
        display_image(image_path)

if __name__ == "__main__":
    enhanced_infinite_chat()