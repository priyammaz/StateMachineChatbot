from emora_stdm import KnowledgeBase, DialogueFlow, NatexNLG, Macro
from enum import Enum, auto


class State(Enum):
    START = auto()
    PROMPT = auto()
    PICK_COLOR = auto()
    ASK_FOOD = auto()
    PICK_FOOD = auto()
    FINAL_RESPONSE = auto()


primary_colors = {"red", "blue", "yellow"}
secondary_colors = {"green", "purple", "orange", "white", "black", "pink"}
colors = {i for j in (primary_colors, secondary_colors) for i in j}

vegetarian_food = {"cereal", "pasta", "pizza", "sushi"}
meat_food = {"chicken", "hamburgers", "fish"}
food = {i for j in (vegetarian_food, meat_food) for i in j}

ontology = {
    "ontology": {
        "ontColors":
            list(colors),
        "ontFood":
            list(food)
    }
}

color_natex = r"[$color=#ONT(ontColors)]"
food_natex = r"[$food=#ONT(ontFood)]"


class ExampleMacro(Macro):

    def __init__(self, check_primary_colors, check_vegetarian_foods):
        self.check_primary_colors = check_primary_colors
        self.check_vegetarian_foods = check_vegetarian_foods

    def run(self, ngrams, variables, args):

        result = ""

        if args[0] in variables:
            favorite_color = variables[args[0]]
            result += "Your favorite color is "
            if favorite_color not in self.check_primary_colors:
                result += "NOT "
            result += "a primary color. "
        else:
            result += "I do not recognize your favorite color. "

        if args[1] in variables:
            favorite_food = variables[args[1]]
            result += "Your favorite food is "
            if favorite_food not in self.check_vegetarian_foods:
                result += "NOT "
            result += "a vegetarian food."
        else:
            result += "I do not recognize your favorite food."

        return result


knowledge = KnowledgeBase()
knowledge.load_json(ontology)
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.SYSTEM, kb=knowledge)

######################################################################
df.add_system_transition(State.START, State.PROMPT, '"Hi, what is your favorite color"')

df.add_user_transition(State.PROMPT, State.PICK_COLOR, color_natex)
df.set_error_successor(State.PROMPT, State.PICK_COLOR)

df.add_system_transition(State.PICK_COLOR, State.ASK_FOOD, '"And what is your favorite food?"')

df.add_user_transition(State.ASK_FOOD, State.PICK_FOOD, food_natex)
df.set_error_successor(State.ASK_FOOD, State.PICK_FOOD)

df.add_system_transition(State.PICK_FOOD, State.FINAL_RESPONSE,
                         NatexNLG('[! #Macro(color, food)]', macros={'Macro': ExampleMacro(primary_colors,
                                                                                           vegetarian_food)}))

df.add_user_transition(State.FINAL_RESPONSE, State.START, color_natex)
df.set_error_successor(State.FINAL_RESPONSE, State.START)

######################################################################

if __name__ == '__main__':
    df.run(debugging=False)
