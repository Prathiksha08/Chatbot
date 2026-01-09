# AI Game Referee: Rock-Paper-Scissors-Plus

An intelligent chatbot referee that manages a Rock-Paper-Scissors-Plus game using Google's Gemini AI and the ADK (AI Development Kit).

## State Model

The game state is maintained as a Python dictionary with the following structure:

```python
game_state = {
    "round": 1,                    # Current round (1-3)
    "user_score": 0,              # User's score
    "bot_score": 0,               # Bot's score  
    "user_bomb_used": False,      # Whether user used their bomb
    "bot_bomb_used": False,       # Whether bot used its bomb
    "history": []                 # List of round results
}
```

**Key Design Decisions:**
- State persists across rounds via a global `game_state` dictionary
- Bomb usage is tracked separately for user and bot to prevent multiple uses
- History maintains a complete record for debugging and game review
- Round counter automatically advances and enforces 3-round limit

## Agent/Tool Design

### Architecture Overview

The solution follows a clean separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Intent          │    │ Game Logic       │    │ Response         │
│ Understanding   │    │ Validation       │    │ Generation       │
│                 │    │                  │    │                  │
│ • Parse user    │────▶ validate_move    │────▶ Natural language │
│   input         │    │ • resolve_round  │    │   feedback       │
│ • Understand    │    │ • update_state   │    │ • Round results  │
│   game context  │    │                  │    │ • Score updates  │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

### ADK Tools

Three explicit tools handle core game logic:

#### 1. `validate_move_func(user_input, user_bomb_used)`
**Purpose:** Intent understanding and input validation
- Normalizes user input (lowercase, trim)
- Validates against allowed moves: rock, paper, scissors, bomb
- Enforces bomb usage limit (once per game)
- Returns structured validation result

#### 2. `resolve_round_func(user_move, bot_bomb_used)`  
**Purpose:** Game logic and outcome determination
- Bot makes intelligent move (15% bomb probability if available)
- Implements game rules:
  - Bomb beats all except bomb
  - Bomb vs bomb = draw
  - Standard RPS rules otherwise
- Handles invalid moves (bot wins wasted rounds)
- Returns round outcome

#### 3. `update_game_state_func(state, user_move, bot_move, winner)`
**Purpose:** State mutation and progression
- Updates bomb usage tracking
- Increments scores based on winner
- Records round history
- Advances round counter
- Returns updated state

### Agent Workflow

1. **Gemini AI** receives user input and current game state
2. **Intent Understanding:** AI decides which tools to call based on input
3. **Tool Execution:** Python functions handle validation, logic, and state updates
4. **Response Generation:** AI synthesizes tool outputs into natural language

## Tradeoffs Made

### 1. State Management
**Decision:** Global dictionary vs. class-based state  
**Tradeoff:** Simplicity vs. encapsulation  
**Rationale:** Global state is simpler for a 3-round game, though a GameState class would be better for larger applications

### 2. Bot Intelligence  
**Decision:** Random moves with 15% bomb probability  
**Tradeoff:** Simplicity vs. strategic AI  
**Rationale:** Focuses on referee logic rather than game AI. Real strategy would require move prediction and game theory

### 3. Error Handling
**Decision:** Graceful degradation vs. strict validation  
**Tradeoff:** User experience vs. rule enforcement  
**Rationale:** Invalid inputs waste rounds rather than causing crashes, maintaining game flow

### 4. API Key Management
**Decision:** Environment variable with fallback  
**Tradeoff:** Security vs. ease of demo  
**Rationale:** Supports secure deployment while allowing quick testing with fallback key

## What I Would Improve With More Time

### 1. Enhanced Bot Strategy
- Implement pattern recognition to counter user tendencies
- Add difficulty levels (random, adaptive, strategic)
- Consider game theory optimal play

### 2. Better State Management  
```python
class GameState:
    def __init__(self):
        self.round = 1
        self.scores = {"user": 0, "bot": 0}
        self.bomb_used = {"user": False, "bot": False}
        self.history = []
    
    def is_game_over(self) -> bool:
        return self.round > 3
```

### 3. Comprehensive Testing
- Unit tests for each tool function
- Integration tests for game scenarios
- Edge case testing (invalid inputs, API failures)

### 4. Configuration Management
- Move game rules to config file
- Support different game variants
- Adjustable round limits and rules

### 5. Enhanced User Experience
- ASCII art for moves
- Colorized output
- Game statistics and analytics

## Running the Game

### Option 1: Direct Python
```bash
# Set environment variable (Windows)
set GEMINI_API_KEY=your_key_here
python main.py

# Set environment variable (Linux/Mac)  
export GEMINI_API_KEY=your_key_here
python main.py
```

### Option 2: Batch Script (Windows)
```bash
run_game.bat
```

## Requirements Compliance

✅ **Game Flow:** 5-line rule explanation, move prompts, validation, outcomes  
✅ **Logic Constraints:** Bomb limits, invalid handling, 3-round limit, state persistence  
✅ **Technical:** Python + Google ADK, explicit tools, no external dependencies  
✅ **Architecture:** Clear separation of intent/logic/response  
✅ **Output:** Round-by-round feedback, explicit move/winner indication  

## Dependencies

```
google-generativeai>=0.3.0
```

Install with: `pip install google-generativeai`