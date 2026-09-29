import pandas as pd
import streamlit as st

from evaluator import evaluate_response
from utils import build_record, load_history, save_record, summary_metrics
import json
from pathlib import Path

SAMPLE_CASES = json.loads(Path("data/sample_cases.json").read_text(encoding="utf-8"))

st.set_page_config(page_title="AI Output Quality Evaluator", layout="wide")

st.title("AI Output Quality Evaluator")
st.write("Evaluate AI-generated responses for quality, accuracy, relevance and safety.")
st.subheader("Try a Sample Case")
sample_labels = ["Choose a sample..."] + [case["label"] for case in SAMPLE_CASES]
chosen = st.selectbox("Load example", sample_labels)
if chosen != "Choose a sample...":
    match = next(case for case in SAMPLE_CASES if case["label"] == chosen)
    st.session_state["sample_prompt"] = match["prompt"]
    st.session_state["sample_response"] = match["response"]
original_prompt = st.text_area(
    "Original User Prompt", value=st.session_state.get("sample_prompt", ""), height=120
)
ai_response = st.text_area(
    "AI Generated Response", value=st.session_state.get("sample_response", ""), height=200
)
reference_answer = st.text_area("Reference Answer (Optional)", height=120)

if st.button("Evaluate Response"):
    if not original_prompt.strip() or not ai_response.strip():
        st.warning("Please fill in the prompt and the AI response.")
    else:
        try:
            with st.spinner("Evaluating..."):
                result = evaluate_response(original_prompt, ai_response, reference_answer)
        except Exception as error:
            st.error(f"Something went wrong: {error}")
        else:
            st.session_state["result"] = result
            st.session_state["prompt"] = original_prompt
            st.session_state["saved"] = False

result = st.session_state.get("result")
if result:
    st.subheader("Result")
    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Score", result["overall_score"])
    col2.metric("AI Recommendation", result["decision"])
    col3.metric("Hallucination Risk", result["hallucination_risk"])

    st.subheader("Metric Scores")
    names = ["accuracy", "relevance", "completeness", "clarity",
             "instruction_following", "safety"]
    cols = st.columns(len(names))
    for col, name in zip(cols, names):
        col.metric(name.replace("_", " ").title(), result[name])

    st.subheader("Summary")
    st.write(result["overall_summary"])
    st.markdown("**Strengths**")
    for item in result["strengths"]:
        st.write(f"- {item}")
    st.markdown("**Issues**")
    for item in result["issues"]:
        st.write(f"- {item}")
    st.markdown("**Suggested improvement**")
    st.write(result["suggested_improvement"])

    st.subheader("Human Reviewer")
    st.write(f"AI Recommendation: **{result['decision']}**")
    human_decision = st.radio(
        "Reviewer decision",
        ["Approve", "Needs Correction", "Reject"],
        horizontal=True,
    )
    notes = st.text_area("Reviewer notes", height=80)
    if st.button("Save Review"):
        save_record(build_record(st.session_state["prompt"], result, human_decision, notes))
        st.session_state["saved"] = True
    if st.session_state.get("saved"):
        st.success("Review saved to history.")

st.divider()
st.header("Evaluation History")
history = load_history()
if not history:
    st.info("No saved reviews yet. Evaluate a response and click Save Review.")
else:
    metrics = summary_metrics(history)
    for col, (label, value) in zip(st.columns(len(metrics)), metrics.items()):
        col.metric(label, value)
    st.dataframe(pd.DataFrame(history))