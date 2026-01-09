import random

def validate_move_func(user_input: str, user_bomb_used: bool):
    """
    ADK Tool: Validate user move and ensure bomb is used only once.
    
    Args:
        user_input (str): Raw user input to validate
        user_bomb_used (bool): Whether user has already used bomb
        
    Returns:
        dict: Validation result with is_valid, move, and reason
    """
    user_input = user_input.lower().strip()
    valid_moves = ["rock", "paper", "scissors", "bomb"]

    if user_input not in valid_moves:
        return {"is_valid": False, "move": user_input, "reason": "Invalid move. This round is wasted!"}

    if user_input == "bomb" and user_bomb_used:
        return {"is_valid": False, "move": user_input, "reason": "Bomb already used! This round is wasted!"}

    return {"is_valid": True, "move": user_input, "reason": "Valid move."}

def resolve_round_func(user_move: str, bot_bomb_used: bool):
    """
    ADK Tool: Bot makes its move and determines round winner.
    
    Args:
        user_move (str): User's validated move ('invalid' for wasted rounds)
        bot_bomb_used (bool): Whether bot has already used bomb
        
    Returns:
        dict: Round result with bot_move and winner
    """
    # Logic for wasted round
    if user_move not in ["rock", "paper", "scissors", "bomb"]:
        return {"bot_move": random.choice(["rock", "paper", "scissors"]), "winner": "bot"}

    # Bot uses bomb with 15% probability if available
    bot_move = "bomb" if (not bot_bomb_used and random.random() < 0.15) else random.choice(["rock", "paper", "scissors"])

    # Bomb logic
    if user_move == "bomb" and bot_move == "bomb":
        return {"bot_move": bot_move, "winner": "draw"}
    if user_move == "bomb":
        return {"bot_move": bot_move, "winner": "user"}
    if bot_move == "bomb":
        return {"bot_move": bot_move, "winner": "bot"}

    # Standard RPS logic
    wins = {("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")}
    if user_move == bot_move:
        return {"bot_move": bot_move, "winner": "draw"}
    return {"bot_move": bot_move, "winner": "user"} if (user_move, bot_move) in wins else {"bot_move": bot_move, "winner": "bot"}

def update_game_state_func(state: dict, user_move: str, bot_move: str, winner: str):
    """
    ADK Tool: Updates game state with round results and advances to next round.
    
    Args:
        state (dict): Current game state
        user_move (str): User's move for this round
        bot_move (str): Bot's move for this round  
        winner (str): Round winner ('user', 'bot', or 'draw')
        
    Returns:
        dict: Updated game state with new scores, round history, and incremented round
    """
    # Update bomb usage tracking
    if user_move == "bomb": 
        state["user_bomb_used"] = True
    if bot_move == "bomb": 
        state["bot_bomb_used"] = True

    # Update scores
    if winner == "user": 
        state["user_score"] += 1
    elif winner == "bot": 
        state["bot_score"] += 1

    # Record round history
    state["history"].append({
        "round": state["round"],
        "user_move": user_move,
        "bot_move": bot_move,
        "winner": winner
    })
    
    # Advance to next round
    state["round"] += 1
    return state