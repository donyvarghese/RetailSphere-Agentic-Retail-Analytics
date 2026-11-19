
import streamlit as st
import retail_agent

st.title("🤖 AI Retail Assistant")
st.caption("Ask questions using your local Qwen 2.5 agent.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("tools"):
            st.caption("Tools used: " + ", ".join(message["tools"]))

suggestions = [
    "What is the total revenue?",
    "Show me the top 3 products.",
    "Which state generated the highest revenue?",
    "What percentage of revenue came from the top 3 products?"
]

st.subheader("Suggested questions")

for i, suggestion in enumerate(suggestions):
    if st.button(suggestion, key=f"question_{i}"):
        st.session_state.pending_question = suggestion
        st.rerun()

question = st.chat_input("Ask your retail analytics question...")

if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Analysing retail data..."):
                answer = retail_agent.run_agent(question)
                answer = str(answer)
                used_tools = list(retail_agent.last_tool_calls)

            st.markdown(answer)

            if used_tools:
                st.caption("Tools used: " + ", ".join(used_tools))

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "tools": used_tools
            })

        except Exception as e:
            st.error("Unable to process your question.")
            st.exception(e)
