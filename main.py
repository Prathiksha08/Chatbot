import os
import json
import google.generativeai as genai
from google.ai import generativelanguage as protos 
from tools import validate_move_func, resolve_round_func, update_game_state_func

# ---------------------------------------
# Configuration
# ---------------------------------------
# Get API key from environment variable for security
api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCgZ1AutScN4G-7UjcUi_nz9qWHAvMWqh8')
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable not set!")
    print("Please set your API key: set GEMINI_API_KEY=your_api_key_here")
    exit(1)

genai.configure(api_key=api_key)

# AUTO-DETECT WORKING MODEL (Prefer Gemini Pro models)
working_model = "gemini-1.5-pro"
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # First try to find gemini-1.5-pro
    if any("gemini-1.5-pro" in m for m in available_models):
        working_model = [m for m in available_models if "gemini-1.5-pro" in m][0]
    # Then try other gemini models
    elif any("gemini" in m for m in available_models):
        working_model = [m for m in available_models if "gemini" in m][0]
    # Last resort: any available model
    elif available_models:
        working_model = available_models[0]
    print(f"✅ Using model: {working_model}")
except Exception:
    print(f"⚠️ Attempting with default: {working_model}")

# Game State [cite: 35, 41, 56]
game_state = {
    "round": 1,
    "user_score": 0,
    "bot_score": 0,
    "user_bomb_used": False,
    "bot_bomb_used": False,
    "history": []
}

SYSTEM_PROMPT = """You are an AI Referee for Rock-Paper-Scissors-Plus.
Rules: Best of 3 rounds. Valid moves: rock, paper, scissors, bomb (once per game).
Bomb beats all moves except bomb. Bomb vs bomb = draw. Invalid input wastes round.
You must validate moves, determine winners, update scores, and end after 3 rounds.
Always use the provided tools: validate_move_func, resolve_round_func, update_game_state_func."""

model = genai.GenerativeModel(
    model_name=working_model,
    tools=[validate_move_func, resolve_round_func, update_game_state_func]
)

chat = model.start_chat(history=[
    {"role": "user", "parts": [SYSTEM_PROMPT]},
    {"role": "model", "parts": ["Ready. I will follow the workflow and track the state accurately."]}
], enable_automatic_function_calling=False)

def run_tool(call):
    name = call.name
    args = call.args
    if name == "validate_move_func":
        return validate_move_func(args["user_input"], args["user_bomb_used"])
    elif name == "resolve_round_func":
        return resolve_round_func(args["user_move"], args["bot_bomb_used"])
    elif name == "update_game_state_func":
        # Ensure state is handled as a dict 
        state_dict = json.loads(args["state"]) if isinstance(args["state"], str) else dict(args["state"])
        result = update_game_state_func(state_dict, args["user_move"], args["bot_move"], args["winner"])
        
        # FIX: Explicitly cast back to a standard dict to prevent JSON serialization errors
        game_state.update(json.loads(json.dumps(result, default=lambda x: list(x) if hasattr(x, '__iter__') else str(x))))
        return result

# ---------------------------------------
# Game Loop [cite: 64]
# ---------------------------------------
print("\n🤖 AI Referee Ready!\n")
print("🎮 Rock-Paper-Scissors-Plus Game")
print("Rules: Best of 3 rounds. Valid moves: rock, paper, scissors, bomb (once per game)")
print("Bomb beats all except bomb. Invalid input wastes the round.\n")

try:
    res = chat.send_message(f"Game State: {json.dumps(game_state)}. Start Round 1.")
except Exception as e:
    if "quota" in str(e).lower() or "429" in str(e):
        print("❌ API quota exceeded. Please wait a minute and try again, or check your billing plan.")
        print("Visit https://ai.dev/rate-limit to monitor usage.")
    else:
        print(f"❌ Error starting game: {e}")
    exit(1)

while game_state["round"] <= 3:
    print(f"Referee: {res.text}")
    user_in = input("\nYou: ")
    
    try:
        # Send user message with current state 
        res = chat.send_message(f"User: {user_in}. State: {json.dumps(game_state)}")
        
        while res.candidates[0].content.parts[0].function_call:
            call = res.candidates[0].content.parts[0].function_call
            out = run_tool(call)
            
            res = chat.send_message(
                protos.Content(
                    parts=[protos.Part(
                        function_response=protos.FunctionResponse(name=call.name, response={"result": out})
                    )]
                )
            )
    except Exception as e:
        if "quota" in str(e).lower() or "429" in str(e):
            print("\n❌ API quota exceeded. Game ending early.")
            print("Please wait and try again, or upgrade your API plan.")
            break
        else:
            print(f"\n❌ Error during game: {e}")
            print("Game ending early.")
            break

# Final Result [cite: 36, 82]
print(f"\n--- Final Results ---")
print(f"Final Score -> You: {game_state['user_score']} | Bot: {game_state['bot_score']}")
if game_state['user_score'] > game_state['bot_score']: print("🎉 You Win!")
elif game_state['user_score'] < game_state['bot_score']: print("🤖 Bot Wins!")
else: print("🤝 It's a Draw!")