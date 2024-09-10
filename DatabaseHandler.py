import sqlite3
class DatabaseHandler:
    def __init__(self, db_name='agent_memory.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS factual_memory
        (id INTEGER PRIMARY KEY, timestamp TEXT, fact TEXT)
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotional_memory
        (id INTEGER PRIMARY KEY, timestamp TEXT, event_summary TEXT)
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_summaries
        (id INTEGER PRIMARY KEY, timestamp TEXT, summary TEXT)
        ''')
        self.conn.commit()

    def add_factual_memory(self, timestamp, fact):
        self.cursor.execute('INSERT INTO factual_memory (timestamp, fact) VALUES (?, ?)',
                            (timestamp, fact))
        self.conn.commit()

    def add_emotional_memory(self, timestamp, event_summary):
        self.cursor.execute('INSERT INTO emotional_memory (timestamp, event_summary) VALUES (?, ?)',
                            (timestamp, event_summary))
        self.conn.commit()

    def get_factual_memories(self):
        self.cursor.execute('SELECT timestamp, fact FROM factual_memory')
        return self.cursor.fetchall()

    def get_emotional_memories(self):
        self.cursor.execute('SELECT timestamp, event_summary FROM emotional_memory')
        return self.cursor.fetchall()
    
    def add_conversation_summary(self, timestamp, summary):
        self.cursor.execute('INSERT INTO conversation_summaries (timestamp, summary) VALUES (?, ?)',
                            (timestamp, summary))
        self.conn.commit()

    def get_latest_conversation_summary(self):
        self.cursor.execute('SELECT timestamp, summary FROM conversation_summaries ORDER BY timestamp DESC LIMIT 1')
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()