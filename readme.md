# AI Output Quality Evaluator

A Streamlit app for reviewing AI-generated responses with a repeatable, human-in-the-loop quality workflow. The evaluator uses Google Gemini to score a response, applies deterministic scoring and routing rules in Python, and lets a human reviewer make the final decision.

## What it does

1. Enter an original user prompt and an AI-generated response.
2. Optionally provide a reference answer.
3. Ask Gemini to assess the response across six quality dimensions.
4. Calculate a weighted overall score and route the result to `PASS`, `HUMAN REVIEW`, or `FAIL`.
5. Review the evidence, record a human decision, and save the review to the local history dashboard.

The application keeps the model's assessment separate from the final human decision, making the workflow easier to audit and improve.

## Features

- Structured JSON evaluations instead of free-form model output
- Scores from 0–100 for:
  - Accuracy
  - Relevance
  - Completeness
  - Clarity
  - Instruction following
  - Safety
- Hallucination-risk classification: `Low`, `Medium`, or `High`
- Deterministic weighted score and decision thresholds
- Human reviewer actions: `Approve`, `Needs Correction`, or `Reject`
- Built-in sample cases for quick demonstrations
- Local evaluation history with total evaluations, average score, pass rate, human-review rate, and failure rate
- Model fallback and retry handling for transient Gemini errors

## Scoring and routing

The overall score is calculated in Python after the model returns its dimension scores:

| Dimension | Weight |
| --- | ---: |
| Accuracy | 25% |
| Relevance | 20% |
| Completeness | 15% |
| Clarity | 10% |
| Instruction following | 20% |
| Safety | 10% |

Routing thresholds:

- `85–100`: `PASS`
- `70–84.9`: `HUMAN REVIEW`
- Below `70`: `FAIL`

The final reviewer decision is saved alongside the AI recommendation so the two outcomes can be compared later.

## Requirements

- Python 3.10 or newer
- A Google Gemini API key

## Local setup

```bash
git clone https://github.com/nikita-primadsouza/ai-output-quality-evaluator.git
cd ai-output-quality-evaluator

python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\\Scripts\\activate      # Windows PowerShell

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
# Optional: override the first model used by the evaluator
GEMINI_MODEL=gemini-3.5-flash
```

Never commit `.env` or expose the API key in a public repository.

## Run the app

```bash
streamlit run app.py
```

Streamlit will print a local URL, normally `http://localhost:8501`.

## Using the app

1. Choose a built-in sample case or enter a prompt and response manually.
2. Add a reference answer when you have an authoritative expected result.
3. Select **Evaluate Response**.
4. Inspect the overall score, dimension scores, hallucination risk, strengths, issues, and suggested improvement.
5. Select a reviewer decision, add notes, and choose **Save Review**.
6. Use the history section to review aggregate metrics and saved records.

## Project structure

```text
.
├── app.py                    # Streamlit interface and reviewer workflow
├── evaluator.py              # Gemini calls, retries, weighted score, routing
├── prompts.py                # Structured evaluation prompt
├── utils.py                  # History persistence and summary metrics
├── requirements.txt          # Python dependencies
└── data/
    ├── sample_cases.json     # Demonstration inputs
    └── evaluation_history.json # Local saved reviews
```

`data/evaluation_history.json` is created or updated when a reviewer saves a result. It is local, file-based storage intended for demos and prototypes; it is not a multi-user database.

## Architecture

```text
User prompt + AI response + optional reference
                    ↓
             Gemini evaluation
                    ↓
       Structured scores and review evidence
                    ↓
       Python weighted score + decision rules
                    ↓
       PASS / HUMAN REVIEW / FAIL recommendation
                    ↓
          Human decision and audit history
```

## Design notes and limitations

- Gemini produces the initial assessment; the application does not treat that assessment as the final approval.
- A reference answer is optional, so factual accuracy can be harder to judge for open-ended prompts.
- Saved history is stored in a local JSON file and can be lost or conflicted when multiple users write at once.
- API availability, model quotas, and model behavior can affect evaluation results.
- For production use, add authentication, durable storage, request logging, rate limits, privacy controls, and a test set with known labels.

## License

No license has been added yet. Add a `LICENSE` file before distributing or accepting external contributions.
