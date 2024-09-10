from Const import PERSONA_PROMPT, MODEL_NAME

class FriendAgent:
    def __init__(self, memory_manager, client):
        self.memory_manager = memory_manager
        self.client = client
        self.send_greeting()

    def respond(self, user_input):
        self.memory_manager.add_to_conversation_history("user", user_input)
        
        factual_memories = self.memory_manager.factual_memory
        emotional_memories = self.memory_manager.get_emotional_memory()
        latest_summary = self.memory_manager.get_latest_conversation_summary()
        
        system_message = self.get_system_message(factual_memories, emotional_memories, latest_summary)
        
        response = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=300,
            system=system_message,
            messages=self.memory_manager.get_conversation_history()
        )
        
        ai_response = response.content[0].text
        self.memory_manager.add_to_conversation_history("assistant", ai_response)
        
        return ai_response

    def get_system_message(self, factual_memories, emotional_memories, latest_summary):
        # Handle factual memories
        if isinstance(factual_memories, list) and factual_memories and isinstance(factual_memories[0], dict):
            factual_texts = [memory.get('fact', '') for memory in factual_memories]
        elif isinstance(factual_memories, str):
            factual_texts = [factual_memories]
        else:
            factual_texts = []

        # Handle emotional memories
        if isinstance(emotional_memories, list) and emotional_memories and isinstance(emotional_memories[0], dict):
            emotional_texts = [memory.get('event_summary', '') for memory in emotional_memories]
        elif isinstance(emotional_memories, str):
            emotional_texts = [emotional_memories]
        else:
            emotional_texts = []

        system_message = f"""{PERSONA_PROMPT}. Use these memories and previous conversation summary to inform your responses:

Factual Memories: {', '.join(factual_texts) if factual_texts else 'No factual memories available.'}
Recent Emotional Memories: {', '.join(emotional_texts) if emotional_texts else 'No emotional memories available.'}
"""
        if latest_summary:
            system_message += f"\nPrevious Conversation Summary: {latest_summary[1] if isinstance(latest_summary, tuple) else latest_summary}"
        else:
            system_message += "\nThis is the first conversation with this user."

        system_message += "\n\nMaintain a consistent personality throughout the conversation."
        return system_message

    def send_greeting(self):
        factual_memories = self.memory_manager.factual_memory
        emotional_memories = self.memory_manager.get_emotional_memory()
        latest_summary = self.memory_manager.get_latest_conversation_summary()
        
        system_message = self.get_system_message(factual_memories, emotional_memories, latest_summary)
        
        conversation_history = self.memory_manager.get_conversation_history()
        
        response = self.client.messages.create(
            model=MODEL_NAME,
            max_tokens=150,
            system=system_message,
            messages=conversation_history + [
                {"role": "user", "content": "🙋‍♀️ Please introduce yourself and greet me based on the provided memories and any previous conversation summary if available."}
            ]
        )
        
        greeting_message = response.content[0].text
        print("🤖 AI: " + greeting_message)
        self.memory_manager.add_to_conversation_history("user", "🙋‍♀️ User starts the conversation.")
        self.memory_manager.add_to_conversation_history("assistant", greeting_message)
    