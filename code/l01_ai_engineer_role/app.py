"""Compare a prototype and a review workflow using a fixed model stub."""

import argparse


def fake_model(category):
    if category == "refund":
        return "Your refund has been approved."
    return "I can help you check your delivery."


def prototype_reply(category):
    return fake_model(category)


def route_reply(category, draft):
    if category != "shipping":
        return "human_review", ""
    if not isinstance(draft, str) or not draft.strip():
        return "human_review", ""
    return "staff_draft", draft.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prototype", action="store_true",
                        help="show the unfiltered refund draft")
    args = parser.parse_args()
    if args.prototype:
        print(f"refund -> {prototype_reply('refund')}")
        return

    # These categories stand in for staff-assigned ticket metadata.
    for category in ("shipping", "refund", "unknown"):
        destination, text = route_reply(category, fake_model(category))
        print(f"{category} -> {destination}")
        if text:
            print(f"  {text}")


if __name__ == "__main__":
    main()
