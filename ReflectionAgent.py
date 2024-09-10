from Const import PERSONA_IMAGE_GEN_PROMPT, MODEL_NAME

class ReflectionAgent:
    def __init__(self, memory_manager, client):
        self.memory_manager = memory_manager
        self.client = client

    def reflect_for_image_generation(self):
        #print("🎨 Reflecting on the conversation for image generation")
        conversation_history = self.memory_manager.get_conversation_history()
        
        # Get the full conversation context
        full_context = "\n".join([f"{'Rick' if msg['role'] == 'assistant' else 'User'}: {msg['content']}" for msg in conversation_history])
        
        # Get the last 2-3 messages
        recent_messages = conversation_history[-2:]
        recent_context = "\n".join([f"{'Rick' if msg['role'] == 'assistant' else 'User'}: {msg['content']}" for msg in recent_messages])
        
        # Extract memories
        factual_memories = self.memory_manager.factual_memory
        emotional_memories = self.memory_manager.get_emotional_memory()

        # Process factual memories
        if isinstance(factual_memories, list) and factual_memories and isinstance(factual_memories[0], dict):
            factual_texts = [memory.get('fact', '') for memory in factual_memories]
        elif isinstance(factual_memories, str):
            factual_texts = [factual_memories]
        else:
            factual_texts = []

        # Process emotional memories
        if isinstance(emotional_memories, list) and emotional_memories and isinstance(emotional_memories[0], dict):
            emotional_texts = [memory.get('event_summary', '') for memory in emotional_memories]
        elif isinstance(emotional_memories, str):
            emotional_texts = [emotional_memories]
        else:
            emotional_texts = []

        # Combine memories
        user_context = "User's Factual Information:\n" + "\n".join(factual_texts) + "\n\nUser's Emotional Information:\n" + "\n".join(emotional_texts)

        response = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=600,  # Requesting more tokens to ensure we get at least 500 characters
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this conversation between Rick Sanchez and a user from a third-party perspective:

Rick Sanchez's personality:
{PERSONA_IMAGE_GEN_PROMPT}
User's context:
{user_context}

Full conversation:
{full_context}

Recent messages:
{recent_context}

Create a vivid, descriptive summary of the conversation's content and mood in exactly 500 characters, as if describing a scene for an image. 
Focus on visual elements, emotions, and key concepts that could be represented visually.
Include relevant details about Rick's behavior and appearance, the user's reactions, and any abstract or sci-fi elements mentioned.
Describe the scene as if you're a neutral observer, capturing the essence of the interaction between Rick and the user.
Your response should be exactly 500 characters long, not including this instruction."""
                }
            ]
        )
        
        image_gen_text = response.content[0].text.strip()
        
        # Ensure the text is exactly 500 characters
        if len(image_gen_text) > 1000:
            image_gen_text = image_gen_text[:1000]
        
        ##print(f"🖼️ Image Generation Text (500 chars): {image_gen_text}")
        return image_gen_text
    
    def reflect_on_thread(self):
        print("🤔 Reflecting on the conversation thread with context")
        conversation_history = self.memory_manager.get_conversation_history()
        
        contextual_messages = []
        for i in range(len(conversation_history)):
            if conversation_history[i]['role'] == 'user':
                if i > 0 and conversation_history[i-1]['role'] == 'assistant':
                    contextual_messages.append(f"AI: {conversation_history[i-1]['content']}")
                contextual_messages.append(f"User: {conversation_history[i]['content']}")
        
        conversation_context = "\n".join(contextual_messages)
        
        response = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this conversation thread:

{conversation_context}

Extract crucial factual information and significant emotional content about the user.
Use the AI's questions for context, but focus on the user's responses and information about the user.
Even brief statements like "I love cars" should be captured as they provide important insights.
Respond in the following format, with each item on a new line:
EMOTIONAL: [emotional observation]
FACTUAL: [factual information]

Be concise, but make sure to include all relevant details about the user, even from brief statements.

Example response:
EMOTIONAL: User enthusiastic about cars
FACTUAL: User loves cars
EMOTIONAL: User excited about car performance
FACTUAL: User's favorite Audi model is RS6 Avant

If there's no clear emotional content, still include factual information.
If there's no clear factual information, still include emotional observations.
Always provide at least one EMOTIONAL and one FACTUAL observation, even if they are very basic."""
                }
            ]
        )
        
        try:
            reflection_result = self.parse_reflection(response.content[0].text)
            print(f"🧠 Reflection Result: {reflection_result}")
            
            for memory_type, memory_content in reflection_result:
                if memory_type == 'FACTUAL':
                    self.memory_manager.add_factual_memory(memory_content)
                elif memory_type == 'EMOTIONAL':
                    self.memory_manager.add_emotional_memory(memory_content)
            
            return reflection_result
        except Exception as e:
            print(f"Error during reflection: {e}")
            return None

    def parse_reflection(self, reflection_text):
        print("🔍 Parsing reflection text:", reflection_text)
        lines = reflection_text.strip().split('\n')
        parsed_reflection = []
        for line in lines:
            if line.startswith('EMOTIONAL:'):
                parsed_reflection.append(('EMOTIONAL', line[10:].strip()))
            elif line.startswith('FACTUAL:'):
                parsed_reflection.append(('FACTUAL', line[8:].strip()))
        return parsed_reflection
    
    def summarize_conversation(self):
        print("📚 Summarizing the entire conversation")
        conversation_history = self.memory_manager.get_conversation_history()
        
        conversation_context = self.memory_manager.get_latest_conversation_summary()[1] + "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])
        
        response = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=600,
            messages=[
                {
                    "role": "user",
                    "content": f"""Summarize this conversation in 600 characters or less:

{conversation_context}

Focus on the main topics discussed and any key points or conclusions reached."""
                }
            ]
        )
        
        summary = response.content[0].text.strip()
        print(f"📝 Conversation Summary: {summary}")
        return summary
