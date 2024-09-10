
from DatabaseHandler import DatabaseHandler
from datetime import datetime

class MemoryManager:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.factual_memory = []
        self.emotional_memory = []
        self.conversation_history = []
        self.load_memories()

    def load_memories(self):
        for timestamp, fact in self.db_handler.get_factual_memories():
            self.factual_memory.append({
                "timestamp": timestamp,
                "fact": fact
            })
        for timestamp, event_summary in self.db_handler.get_emotional_memories():
            self.emotional_memory.append({
                "timestamp": timestamp,
                "event_summary": event_summary
            })

    def add_factual_memory(self, fact):
        timestamp = datetime.now().isoformat()
        self.factual_memory.append({
            "timestamp": timestamp,
            "fact": fact
        })
        self.db_handler.add_factual_memory(timestamp, fact)
        print(f"📚 Factual Memory Added: {fact}")

    def add_emotional_memory(self, event_summary):
        timestamp = datetime.now().isoformat()
        self.emotional_memory.append({
            "timestamp": timestamp,
            "event_summary": event_summary
        })
        self.db_handler.add_emotional_memory(timestamp, event_summary)
        print(f"😊 Emotional Memory Added: {event_summary}")

    def add_to_conversation_history(self, role, content):
        self.conversation_history.append({"role": role, "content": content})

    def get_factual_memory(self, key):
        return self.factual_memory.get(key, "No information found.")

    def get_emotional_memory(self, limit=5):
        return sorted(self.emotional_memory, key=lambda x: x['timestamp'], reverse=True)[:limit]

    def get_conversation_history(self):
        return self.conversation_history
    
    def add_conversation_summary(self, summary):
        timestamp = datetime.now().isoformat()
        self.db_handler.add_conversation_summary(timestamp, summary)
        print(f"📝 Conversation Summary Added: {summary}")

    def get_latest_conversation_summary(self):
        return self.db_handler.get_latest_conversation_summary()
