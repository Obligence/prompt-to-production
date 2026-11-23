# Lesson 11 (Module 4): Your First LLM Call
# Reference lesson: uses every scene kind. Copy this file to start a new lesson.

LESSON = dict(
    number=11, module=4, slug="l11_first_llm_call",
    title="Your First LLM Call",
    cover_text="Your first|LLM call",
    next="Lesson 12: Build a chatbot with memory",
)

SETUP = """# create the project
uv init first-llm-app && cd first-llm-app
uv add anthropic

# keep the key out of your code
export ANTHROPIC_API_KEY="sk-ant-..." """

FIRST_CALL = """from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=500,
    system="You are a friendly coding tutor.",
    messages=[
        {"role": "user", "content": "Explain an API in one sentence."}
    ],
)

print(response.content[0].text)"""

ANATOMY = """print(response.content[0].text)   # the answer
print(response.stop_reason)       # "end_turn" or "max_tokens"
print(response.model)             # which model answered

usage = response.usage
print(usage.input_tokens)         # what you sent
print(usage.output_tokens)        # what you got back"""

COST = """# prices change: copy them from your provider's pricing page
PRICE_IN = 3.00     # dollars per million input tokens
PRICE_OUT = 15.00   # dollars per million output tokens

def call_cost(usage):
    return (usage.input_tokens * PRICE_IN
            + usage.output_tokens * PRICE_OUT) / 1_000_000

print(f"This call cost ${call_cost(response.usage):.5f}")"""

SCENES = [
    dict(kind="title", steps=[
        ("Welcome to Prompt to Production. This is lesson eleven of the free course, How to Become an AI Application Engineer. "
         "Today, you'll write your first program that talks to a large language model. And by the end, you'll understand every line of it.", 0),
    ]),
    dict(kind="bullets", title="By the end of this lesson", chapter="What you'll learn", style="goal",
         side={"terminal": [["$ uv run app.py", "teal"], ["An API is a contract that lets", "violet"],
                            ["one program ask another for", "violet"], ["data or actions.", "violet"],
                            ["", "fg"], ["stop_reason: end_turn", "muted"], ["tokens: 24 in · 19 out", "muted"]]},
         steps=[
             ("Here's what you'll be able to do by the end of this lesson.", None),
             ("Call an LLM from Python, with your API key stored safely.", "Call an LLM safely from Python"),
             ("Understand each part of the request you send.", "Understand every part of the request"),
             ("Read the response, including the tokens you just paid for.", "Read the response and its tokens"),
             ("And work out what each call costs, so you never get a surprise bill.", "Work out what each call costs"),
         ]),
    dict(kind="flow", title="What happens when you call an LLM", chapter="How an LLM call works",
         subtitle="An LLM call is just an HTTPS request with a JSON body.",
         boxes=[["Your code", "Python app with the SDK", "data"],
                ["Request", "model, system prompt, messages, max tokens", "user"],
                ["LLM provider", "runs the model on its servers", "system"],
                ["Response", "text, stop reason, token usage", "bot"]],
         callout="The SDK only builds this request for you. There's no magic in between.",
         steps=[
             ("Before we write code, let's see what actually happens. Your code uses the provider's SDK, which is just a small library.", 1),
             ("The SDK sends a request over HTTPS. Inside it: which model to use, a system prompt, the conversation messages, and a limit on how long the answer can be.", 2),
             ("The provider runs the model on its own servers. You never download the model.", 3),
             ("And you get a response back, with the generated text, the reason the model stopped, and how many tokens were used. "
              "That's it. The SDK only builds this request for you. There's no magic in between.", 4),
         ]),
    dict(kind="code", title="Step 1 · Set up the project", chapter="Project setup", lang="bash", file="terminal", code=SETUP,
         steps=[
             ("Let's set up the project. I'm using uv, a fast Python package manager. Create a new project, and add the Anthropic SDK.", 3),
             ("Then put your API key in an environment variable. Never paste a key into your code. "
              "Code gets committed, pushed and shared, and leaked keys are found and abused within minutes.", 99),
         ]),
    dict(kind="code", title="Step 2 · Your first call", chapter="Your first call", file="app.py", code=FIRST_CALL,
         steps=[
             ("Here's the whole program. First, create a client. It picks up your key from the environment automatically.", 4),
             ("Then call messages dot create. You choose a model, and max tokens, which caps how long the answer can be. "
              "That also caps what you pay for the answer.", 8),
             ("The system prompt sets the model's role and rules for the whole conversation. "
              "The messages list is the conversation itself. Right now, it's a single user message.", 13),
             ("Finally, print the text of the first content block. That's the answer.", 99),
         ]),
    dict(kind="terminal", title="Run it", chapter="Running the app", file="terminal",
         lines=[["$ uv run app.py", "teal"],
                ["An API is a set of rules that lets one program request", "fg"],
                ["data or actions from another, without knowing how it", "fg"],
                ["works inside.", "fg"],
                ["", "fg"],
                ["$ uv run app.py", "teal"],
                ["An API is like a waiter: you place an order, and it", "fg"],
                ["brings back what the kitchen made.", "fg"]],
         steps=[
             ("Now run it. In a second or two, the answer comes back.", 4),
             ("Run it again, and you'll probably get a different answer. That's normal. "
              "The model samples its words, so the output varies from call to call. Your code has to be ready for that.", 99),
         ]),
    dict(kind="code", title="Step 3 · Read the whole response", chapter="Reading the response", file="app.py", code=ANATOMY,
         steps=[
             ("Don't just grab the text, though. The response tells you much more.", 1),
             ("Stop reason tells you why the model stopped. End turn means it finished. "
              "Max tokens means it hit your limit, and the answer was cut off. Always check this one.", 3),
             ("And usage gives you the input and output tokens. Tokens are pieces of words, and they're exactly what you're billed for. "
              "Professional AI engineers log these numbers from day one.", 99),
         ]),
    dict(kind="code", title="Step 4 · What did that cost?", chapter="Calculating cost", file="cost.py", code=COST,
         steps=[
             ("So let's turn tokens into money. Providers charge per million tokens, and output tokens usually cost more than input tokens. "
              "Prices change, so copy the current ones from your provider's pricing page.", 3),
             ("Then a tiny function does the math. Multiply each token count by its price, and divide by a million.", 8),
             ("A single call like ours costs a tiny fraction of a cent. But an app with thousands of users makes millions of calls, "
              "so this function will matter a lot later.", 99),
         ]),
    dict(kind="rows", title="One surprise: the model forgets", chapter="Why the model forgets",
         subtitle="Every API call starts from zero.",
         headline="Stateless", headline_sub="Call 2 has no idea what Call 1 said.",
         rows=[{"label": "Call 1", "chips": [["You: My name is Reza", "user"]], "arrow": "Nice to meet you, Reza!"},
               {"label": "Call 2", "chips": [["You: What's my name?", "user"]], "arrow": "I don't know your name."}],
         callout="Next lesson: give it memory by sending the conversation history.",
         steps=[
             ("One last thing, and it surprises almost everyone. The model has no memory. Every API call starts from zero.", 1),
             ("Tell it your name in one call. Then, in the next call, ask what your name is. It has no idea, because the second request never contained your name.", 2),
             ("So how do chatbots remember? That's exactly what we'll build in the next lesson.", 3),
         ]),
    dict(kind="bullets", title="Beginner mistakes to avoid", chapter="Mistakes to avoid", style="warn", side="warning",
         steps=[
             ("Before you go, four beginner mistakes to avoid.", None),
             ("Hardcoding your API key in the source code.", "Hardcoding the API key"),
             ("Ignoring the stop reason, and shipping answers that were cut off.", "Ignoring the stop reason"),
             ("Not tracking tokens, and finding out about cost from your bill.", "Not tracking tokens and cost"),
             ("And assuming the model remembers earlier calls. It doesn't.", "Assuming the model remembers"),
         ]),
    dict(kind="outro", title="Your homework", chapter="Homework",
         tasks=["Make your first call", "Print tokens and cost", "Try 3 system prompts"],
         steps=[
             ("Your homework: make your first call, print the tokens and the cost of every call, "
              "and try three different system prompts to see how they change the answer. The full code is in the GitHub repo linked below.", 0),
             ("In the next lesson, we'll give the model a memory, and build a real chatbot. Subscribe so you don't miss it. See you there.", 0),
         ]),
]
