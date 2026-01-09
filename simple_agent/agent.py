from tools import get_random_cocktail

def decide_tool(user_input: str):
    """
    Agent logic:
    decides whether to call a tool
    """
    text = user_input.lower()

    if "surprise" in text or "random" in text:
        return "get_random_cocktail"

    return None

def get_sweet_cocktail():
    return "Strawberry Daiquiri 🍓\nIngredients: Rum, strawberry, lime, sugar"

def show_help():
    return (
        "I can:\n"
        "- Surprise you with a cocktail\n"
        "- Recommend a sweet drink\n"
        "- Help you understand what I can do\n"
        "Try saying: surprise me, something sweet, help"
    )
def decide_tool(user_input):
    user_input = user_input.lower()

    if "surprise" in user_input:
        return "random_cocktail"
    if "sweet" in user_input:
        return "sweet_cocktail"
    if "help" in user_input or "what can you do" in user_input:
        return "help"
    
    return None


def run_agent(user_input):
    tool = decide_tool(user_input)

    if tool == "random_cocktail":
        return get_random_cocktail()
    elif tool == "sweet_cocktail":
        return get_sweet_cocktail()
    elif tool == "help":
        return show_help()
    else:
        return "Sorry, I didn’t understand. Try typing 'help'."



if __name__ == "__main__":
    print("AI Agent started. Type something.\n")

    while True:
        user_input = input("You: ")
        response = run_agent(user_input)
        print("Agent:", response)



