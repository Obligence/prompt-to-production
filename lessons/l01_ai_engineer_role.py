# Lesson 1 · Module 1
LESSON = dict(
    number=1,
    module=1,
    slug="l01_ai_engineer_role",
    title="AI Engineer vs ML Engineer vs Vibe Coder",
    cover_text="AI engineer|vs ML engineer",
    next="Lesson 2: The modern AI app stack in one diagram",
)

PROTOTYPE = """def fake_model(category):
    if category == "refund":
        return "Your refund has been approved."
    return "I can help you check your delivery."


def prototype_reply(category):
    return fake_model(category)"""

ROUTING = """def route_reply(category, draft):
    if category != "shipping":
        return "human_review", ""
    if not isinstance(draft, str) or not draft.strip():
        return "human_review", ""
    return "staff_draft", draft.strip()"""

SCENES = [
    dict(kind="title", steps=[
        ("Your support assistant just said a pending refund was approved. "
         "Today we'll fix the workflow in Python and see what that tells us about being an AI application engineer.", 0),
    ]),
    dict(kind="bullets", title="By the end of this lesson", chapter="What you'll learn", style="goal", side="check",
         steps=[
             ("Welcome to Prompt to Production. This is lesson one of How to Become an AI Application Engineer. "
              "We'll look at one small support assistant through three different lenses.", None),
             ("First, you can explain how improving a model differs from building the application that uses it. "
              "We'll also talk about where AI assisted prototyping fits into that work.", "Compare the work each role owns"),
             ("Second, you'll trace a support ticket through a model draft and an application rule. "
              "The rule answers a practical question. Where should this draft go next?", "Follow a support ticket"),
             ("Finally, you'll run the same failure twice. First in a prototype, then with a rule and a test. "
              "You can follow along with plain Python and the example in the course repository.", "Reproduce and test a failure"),
         ]),
    dict(kind="rows", title="Three ways to work with AI", chapter="AI engineer, ML engineer, and vibe coding",
         subtitle="The same support team can use all three.",
         headline="Ownership", headline_sub="Which outcome are you responsible for?",
         rows=[
             {"label": "AI app", "chips": [["Use a model", "bot"], ["Route the result", "system"]],
              "arrow": "Own the application workflow"},
             {"label": "ML", "chips": [["Prepare data", "data"], ["Evaluate a model", "tool"]],
              "arrow": "Own model and pipeline quality"},
             {"label": "Vibe", "chips": [["Describe the idea", "user"], ["Try generated code", "bot"]],
              "arrow": "Explore a prototype"},
         ],
         callout="The responsibilities overlap. Vibe coding describes a way to prototype.",
         steps=[
             ("Start with ownership. Suppose the support team wants fewer repetitive replies. "
              "We can use a model to draft those replies. We still have to decide which tickets it touches, "
              "where drafts appear, and what happens when it gives us an unusable answer.", 1),
             ("Those choices are the AI application engineer's work in this example. The ML engineer might improve "
              "a model that classifies support tickets. They might curate labeled training data, evaluate a new model "
              "on tickets it hasn't seen, and monitor how it performs after deployment.", 2),
             ("Vibe coding is a way to explore an idea by describing what you want and trying generated code. "
              "It can get a prototype in front of the support team quickly. On a small team, one person may do all of this. "
              "The distinction to remember is the outcome each piece of work is trying to improve.", 3),
         ]),
    dict(kind="flow", title="From ticket to staff review", chapter="The application workflow",
         subtitle="Staff assign the ticket category before the model suggests a reply.",
         boxes=[
             ["Support ticket", "Ticket text and staff-assigned category", "user"],
             ["Model draft", "Suggested reply in ordinary text", "bot"],
             ["Python rule", "Check the category and the draft", "system"],
             ["Staff queue", "Show a draft or request review", "tool"],
         ],
         callout="Staff decide what to send. The app decides where the draft goes.",
         steps=[
             ("Let's follow one ticket. A support worker has already tagged it as shipping or refund. "
              "That category comes from the application. We treat it as an input to the rule.", 1),
             ("A model can help with the wording. For example, a shipping draft might ask the customer for an order number. "
              "A refund case can sound just as polished even when the model has no evidence the refund was approved.", 2),
             ("The Python rule decides which output can be shown to staff as a draft. "
              "Here we only want drafts for routine shipping tickets. For other cases the application requests human review.", 3),
             ("Staff make the final decision about what to send. That gives the prototype a practical boundary. "
              "We can test the routing rule by passing in a category and a draft. The quality of a draft is a separate evaluation.", 4),
         ]),
    dict(kind="code", title="The first prototype", chapter="A prototype with a model stub", file="app.py", code=PROTOTYPE,
         steps=[
             ("The function at the top is our model stub. A stub is a small substitute that always gives us the same answer for the same input. "
              "That makes the example reproducible and lets you run it with the Python standard library. The course makes its first live model call in lesson eleven.", 4),
             ("Look at the last two lines. The prototype returns whatever the stub wrote. "
              "That gives us a quick way to see what a draft might look like. We can also see exactly where the application has to decide how to handle it.", 99),
         ]),
    dict(kind="terminal", title="Reproduce the failure", chapter="The misleading refund draft", file="terminal",
         lines=[
             ["$ python3 app.py --prototype", "teal"],
             ["refund -> Your refund has been approved.", "red"],
         ],
         steps=[
             ("Run the application with the prototype flag. For this transcript we use the refund example on purpose. "
              "The command prints locally so we can inspect the draft in the terminal.", 1),
             ("There's the failure. The draft says the refund was approved even though this is a pending request. "
              "The stub makes that failure repeatable. In an application, fluent text like this can make an unverified claim look ready to act on. "
              "We want the application to route this case to staff and leave the draft out.", 99),
         ]),
    dict(kind="code", title="Put the rule in Python", chapter="Route the draft in Python", file="app.py", code=ROUTING,
         steps=[
             ("Start with the category. Shipping is the only category we've decided to support with drafts in this demo. "
              "Anything else goes to human review. That includes a category our prototype has never seen. "
              "The empty string means the staff review item carries none of the generated wording.", 3),
             ("Then check the draft itself. A missing value or a string made of spaces would give staff nothing useful to review. "
              "The type check also lets us check the text safely before trying to trim it. These checks cover the shape of the result.", 5),
             ("Finally, return the trimmed draft for staff. Someone still needs to check the actual order and decide what to send. "
              "Let's run the same ticket through this version and see what changes.", 99),
         ]),
    dict(kind="terminal", title="Run the regression tests", chapter="The revised run and tests", file="terminal",
         lines=[
             ["$ python3 app.py", "teal"],
             ["shipping -> staff_draft", "fg"],
             ["  I can help you check your delivery.", "muted"],
             ["refund -> human_review", "fg"],
             ["unknown -> human_review", "fg"],
             ["", "fg"],
             ["$ python3 -m unittest -v", "teal"],
             ["test_empty (test_app.RoutingTests.test_empty) ... ok", "fg"],
             ["test_non_text (test_app.RoutingTests.test_non_text) ... ok", "fg"],
             ["test_refund (test_app.RoutingTests.test_refund) ... ok", "fg"],
             ["test_shipping (test_app.RoutingTests.test_shipping) ... ok", "fg"],
             ["test_unknown (test_app.RoutingTests.test_unknown) ... ok", "fg"],
             ["Ran 5 tests", "muted"],
             ["OK", "teal"],
         ],
         steps=[
             ("The shipping ticket produces a draft. The refund ticket still gets that misleading suggestion from the stub. "
              "Now it goes to human review with the generated text withheld. The unknown category follows the same review path.", 5),
             ("Run the tests and you'll see the cases listed by name. The refund test checks both parts of the result. "
              "It expects the human review destination and an empty string where a draft would otherwise go.", 10),
             ("All five tests pass. We've checked the application rule with fixed inputs. "
              "To judge a real model, we would use a separate set of examples and ask whether each draft matches the order facts "
              "and the team's reply guidelines. Those are different questions, and both are worth testing.", 99),
         ]),
    dict(kind="bullets", title="Common mistakes", chapter="Mistakes to avoid", style="warn", side="warning",
         steps=[
             ("Here are three mistakes worth catching on your next prototype.", None),
             ("The first is testing just the smoothest example. A routine shipping ticket can make the app look ready. "
              "Try a refund, a new category, and a blank result before you draw that conclusion.", "Testing only the happy path"),
             ("The second is using a model suggestion as if it were approval. A sentence can sound official. "
              "Use staff or application records to determine whether an action was approved.", "Treating prose as authorization"),
             ("The third is asking one test to answer two questions. Test the routing rule with inputs you control. "
              "Measure draft quality on a set of representative tickets that includes hard cases.", "Mixing routing and quality checks"),
         ]),
    dict(kind="outro", title="Your homework", chapter="Homework and what's next",
         tasks=["Run the prototype", "Add one failure case", "Run the tests"],
         steps=[
             ("Your homework is to run both versions. Then add a test for a blank category with a nonempty draft. "
              "Decide what result you expect first, and check that the test agrees. The example and the run commands are in the repository linked below.", 0),
             ("In lesson two we'll draw the modern AI application stack and find where this routing rule belongs. "
              "If you're following the course in order, that's your next lesson.", 0),
         ]),
]
