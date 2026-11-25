# Lesson 1 · AI Engineer vs ML Engineer vs Vibe Coder

Run this demo from the repository root with Python 3 and its standard library.

```bash
cd code/l01_ai_engineer_role
python3 app.py --prototype
python3 app.py
python3 -m unittest -v
```

The prototype prints an unfiltered refund draft from a stub. The revised flow uses a staff-assigned category to route tickets. A nonempty shipping draft can go to staff for review. Refunds, unknown categories, and missing drafts go to a human with the generated text withheld. Both commands write to the local terminal.

The tests check application routing. A separate evaluation with real model outputs would assess the accuracy and quality of drafts.

**Homework**

Add a test for an empty category with a nonempty draft and verify it routes to human review.
