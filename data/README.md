# AI Output Quality Evaluator

A Human-in-the-Loop web app that evaluates AI-generated responses for quality, accuracy, relevance, and safety, and routes them to Pass, Human Review, or Fail.

## Problem Statement
As AI tools generate more content, teams need a consistent way to check output quality before it reaches users. Manual review alone doesn't scale, and fully automated approval risks letting errors through unnoticed.

## Solution
This app scores AI responses across six weighted quality dimensions using Google's Gemini API, calculates a deterministic overall score in Python, and routes each response to Pass, Human Review, or Fail. A human reviewer can then approve, request correction, or reject the AI's recommendation, and every decision is logged to a history dashboard.

## Key Features
- Structured JSON evaluation (not free-form text)
- Six weighted quality metrics: Accuracy, Relevance, Completeness, Clarity, Instruction Following, Safety
- Hallucination risk classification (Low / Medium / High)
- Deterministic scoring and decision logic, separate from the AI's judgment
- Human-in-the-Loop review with Approve / Needs Correction / Reject
- Evaluation history with summary metrics (Pass Rate, Human Review Rate, Failure Rate)
- Four built-in sample cases for quick testing

## Human-in-the-Loop Workflow
1. AI scores the response and gives a recommendation.
2. A human reviewer sees the AI's recommendation and evidence (scores, strengths, issues).
3. The reviewer makes the final call: Approve, Needs Correction, or Reject.
4. Both the AI recommendation and human decision are saved for audit.

## Architecture
User Prompt → AI Generated Response → AI Quality Evaluator → Structured Evaluation → Quality Score → Decision Engine → PASS / HUMAN REVIEW / FAIL → Human QA Review → Final Decision

## Evaluation Methodology
Each response is scored 0–100 on six dimensions by the Gemini API. The overall score is a weighted average calculated in Python:
- Accuracy: 25%
- Relevance: 20%
- Completeness: 15%
- Clarity: 10%
- Instruction Following: 20%
- Safety: 10%

Decision thresholds: 85+ = PASS, 70–84 = HUMAN REVIEW, below 70 = FAIL.

## Technology Stack
Python, Streamlit, Google Gemini API, Pandas, JSON, python-dotenv

## Installation