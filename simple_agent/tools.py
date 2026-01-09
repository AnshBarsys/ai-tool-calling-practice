import random

def get_random_cocktail():
    """
    Tool function:
    Returns a random cocktail
    """
    cocktails = [
        {"name": "Margarita", "base": "Tequila", "flavor": "Sour"},
        {"name": "Mojito", "base": "Rum", "flavor": "Refreshing"},
        {"name": "Old Fashioned", "base": "Whiskey", "flavor": "Bitter"},
    ]
    return random.choice(cocktails)
