"""Lesson 11: your first LLM call. Run: uv run app.py (needs ANTHROPIC_API_KEY)."""
from anthropic import Anthropic

# prices change: copy them from your provider's pricing page
PRICE_IN = 3.00     # dollars per million input tokens
PRICE_OUT = 15.00   # dollars per million output tokens


def call_cost(usage):
    return (usage.input_tokens * PRICE_IN + usage.output_tokens * PRICE_OUT) / 1_000_000


def main():
    client = Anthropic()  # reads ANTHROPIC_API_KEY

    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        system="You are a friendly coding tutor.",
        messages=[{"role": "user", "content": "Explain an API in one sentence."}],
    )

    print(response.content[0].text)
    print("stop_reason:", response.stop_reason)
    print(f"tokens: {response.usage.input_tokens} in · {response.usage.output_tokens} out")
    print(f"This call cost ${call_cost(response.usage):.5f}")


if __name__ == "__main__":
    main()
