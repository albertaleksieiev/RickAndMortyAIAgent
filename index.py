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
from DatabaseHandler import DatabaseHandler
from MemoryManager import MemoryManager
from ReflectionAgent import ReflectionAgent
from FriendAgent import FriendAgent

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize clients
fake_you_client = fakeyou.FakeYou(False)
fake_you_client.login(os.getenv('FAKEYOU_EMAIL'), os.getenv('FAKEYOU_PASSWORD'))
openAIClient = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize the Anthropic client
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

client = anthropic.Anthropic(api_key=api_key)

def infinite_chat():
    memory_manager = MemoryManager()
    reflection_agent = ReflectionAgent(memory_manager, client)
    friend_agent = FriendAgent(memory_manager, client)

    print("👋 Welcome to the infinite chat! Type 'exit' to end the conversation.")
    
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
    memory_manager = MemoryManager()
    friend_agent = FriendAgent(memory_manager, client)
    reflection_agent = ReflectionAgent(memory_manager, client)

    print("👋 Welcome to the enhanced infinite chat! Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() == 'exit':
            break
        
        response = friend_agent.respond(user_input)

        # Use ThreadPoolExecutor for better thread management
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            image_future = executor.submit(generate_and_display_image, reflection_agent)
            audio_future = executor.submit(generate_and_play_audio, response)

        print("🤖 AI: " + response)

        # Wait for both futures to complete
        concurrent.futures.wait([image_future, audio_future])

    # Perform reflection on the conversation thread at the end of the conversation
    reflection_result = reflection_agent.reflect_on_thread()
    print("🧐 Final Reflection:")
    print(json.dumps(reflection_result, indent=2))
    memory_manager.add_conversation_summary(reflection_agent.summarize_conversation())

def generate_and_display_image(reflection_agent):
    image_path = generate_image(reflection_agent.reflect_for_image_generation())
    if image_path:
        display_image(image_path)

def generate_and_play_audio(response):
    audio_out = generate_and_save_audio(response)
    if audio_out:
        playsound(audio_out)

if __name__ == "__main__":
    enhanced_infinite_chat()