
# 🐍 Slither.io Clone

A Python-based clone of the classic Slither.io game built with Pygame and CustomTkinter for a modern UI launcher.

## 🎮 Game Features

- **Two Game Modes**
  - Single Player: Classic snake gameplay with mines and fruits
  - Two Player: Competitive mode with two snakes on the same screen
- **Modern UI Launcher**
  - Customizable player names
  - Game mode selection
  - Sound and music controls
  - Built-in leaderboard system
- **Gameplay Elements**
  - Smooth snake movement
  - Collectible fruits for growth
  - Dangerous mines to avoid
  - Score tracking system
  - Sound effects and background music

## 🔧 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/HugoDavidRS/GAME_PROYECT.git
   ```

2. **Dependencies**
   The project requires:
   - Python 3.x.  
   - Pygame
   - CustomTkinter
   - SQLite3 (included in Python)

## 🚀 Running the Game

1. Launch the game through the launcher:
   ```bash
   python launcher.py
   ```

2. Use the launcher to:
   - Select game mode (Single/Two Player)
   - Enter player names
   - Toggle sound effects and music
   - View the leaderboard

## 🎯 How to Play

### Controls
- **Player 1:**
  - W: Move Up
  - S: Move Down
  - A: Move Left
  - D: Move Right

- **Player 2 (Two Player Mode):**
  - ↑: Move Up
  - ↓: Move Down
  - ←: Move Left
  - →: Move Right

### Game Rules
1. Collect fruits to grow longer
2. Avoid hitting:
   - Walls
   - Other snakes
   - Your own body
   - Mines (they reduce your length)
3. In Two Player Mode:
   - Compete for fruits
   - Try to block other player's path
   - Highest score wins when both snakes crash

## 📁 Project Structure

```
slither-io-clone/
├── assets/               # Game assets
│   ├── Font/            # Game fonts
│   ├── Sound/           # Sound effects and music
│   └── graphics/        # Snake and item sprites
├── src/                 # Source code
│   ├── services/        # Database services
│   ├── sprites/         # Game objects
│   ├── ui/             # UI components
│   └── constants.py     # Game constants
└── launcher.py          # Game launcher
```

## 🔄 Features & Updates

### Current Features
- Smooth snake movement
- Two-player support
- Mine obstacles
- Sound effects
- Background music
- Score tracking
- Leaderboard system

### Planned Updates
- Online multiplayer support
- Additional power-ups
- More game modes
- Customizable snake skins

## 🤝 Contributing

Feel free to fork this project and submit pull requests with improvements! Some areas that could use enhancement:
- Additional game modes
- New power-ups
- UI improvements
- Performance optimizations

## 📜 License

This project is open-source and available for educational purposes.

## 🙏 Credits

- Game assets and sounds from various open-source resources
- Built with Pygame and CustomTkinter
- Developed by
  Hugo David Rosas Labra

## 🐛 Bug Reports

If you find any bugs or have suggestions, please open an issue in the project repository.
