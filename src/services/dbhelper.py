import sqlite3
import os
import sys

class DatabaseService:
    def __init__(self):
        # Determine the application directory for the database file
        if getattr(sys, 'frozen', False):
            # If running as compiled executable
            application_path = os.path.dirname(sys.executable)
        else:
            # If running as script
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        db_path = os.path.join(application_path, 'snake_scores.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Create the necessary tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, highscore_s INTEGER DEFAULT 0, highscore_m INTEGER DEFAULT 0)''')
        self.conn.commit()
        
    def check_username(self, username, username2=None):
        """
        Check if username(s) exist in the database
        Returns list of existing usernames
        """
        existing_users = []
        
        # Convert to uppercase
        username = username.upper()
        self.cursor.execute("SELECT name FROM players WHERE name = ?", (username,))
        if self.cursor.fetchone():
            existing_users.append(username)
            
        if username2:
            username2 = username2.upper()
            self.cursor.execute("SELECT name FROM players WHERE name = ?", (username2,))
            if self.cursor.fetchone():
                existing_users.append(username2)
                
        return existing_users
            
    def register_new_player(self, username):
        """Register a new player with initial scores of 0"""
        username = username.upper()
        try:
            self.cursor.execute(
                "INSERT INTO players (name, highscore_s, highscore_m) VALUES (?, 0, 0)",
                (username,)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False
            
    def update_score_singleplayer(self, username, score):
        """Update single player score if it's higher than the previous one"""
        username = username.upper()
        self.cursor.execute("SELECT highscore_s FROM players WHERE name = ?", (username,))
        result = self.cursor.fetchone()
        
        if not result:
            # New player, insert record
            self.cursor.execute(
                "INSERT INTO players (name, highscore_s, highscore_m) VALUES (?, ?, 0)",
                (username, score)
            )
        elif score > result[0]:
            # Update if new score is higher
            self.cursor.execute(
                "UPDATE players SET highscore_s = ? WHERE name = ?",
                (score, username)
            )
        
        self.conn.commit()
        
    def update_score_multiplayer(self, username, score):
        """Update multiplayer score if it's higher than the previous one"""
        username = username.upper()
        self.cursor.execute("SELECT highscore_m FROM players WHERE name = ?", (username,))
        result = self.cursor.fetchone()
        
        if not result:
            # New player, insert record
            self.cursor.execute(
                "INSERT INTO players (name, highscore_s, highscore_m) VALUES (?, 0, ?)",
                (username, score)
            )
        elif score > result[0]:
            # Update if new score is higher
            self.cursor.execute(
                "UPDATE players SET highscore_m = ? WHERE name = ?",
                (score, username)
            )
        
        self.conn.commit()
        
    def fetch_leaderboard(self, mode='single'):
        """Fetch top 5 players based on game mode"""
        if mode == 'single':
            self.cursor.execute(
                "SELECT name, highscore_s FROM players ORDER BY highscore_s DESC LIMIT 5"
            )
        else:
            self.cursor.execute(
                "SELECT name, highscore_m FROM players ORDER BY highscore_m DESC LIMIT 5"
            )
            
        return self.cursor.fetchall()
        
    def get_player_scores(self, username):
        """Get a player's current scores"""
        username = username.upper()
        self.cursor.execute(
            "SELECT highscore_s, highscore_m FROM players WHERE name = ?",
            (username,)
        )
        result = self.cursor.fetchone()
        if result:
            return {"single": result[0], "multi": result[1]}
        return {"single": 0, "multi": 0}
        
    def close_connection(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()