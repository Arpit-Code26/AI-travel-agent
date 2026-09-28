import streamlit as st
from langchain_core.messages import HumanMessage
from agent import graph
import json

st.set_page_config(page_title="AI Travel Agent")
st.title("AI Travel Agent")

thread_config = {"configurable": {"thread_id": "1"}}

if "messages" not in st.session_state:
    st.session_state.messages = []

def extract_text(content):
    if not content:
        return ""
    if isinstance(content, str):
        trimmed = content.strip()
        if trimmed.startswith("[") or trimmed.startswith("{"):
            try:
                parsed = json.loads(trimmed)
                if isinstance(parsed, list):
                    return "".join([b.get("text", "") for b in parsed if isinstance(b, dict)])
                if isinstance(parsed, dict):
                    return parsed.get("text", str(parsed))
            except json.JSONDecodeError:
                pass
        return content
    if isinstance(content, list):
        return "".join([b.get("text", "") for b in content if isinstance(b, dict)])
    return str(content)

def extract_tool_itinerary(tool_call):
    args = tool_call.get("args", {})
    # Search common parameter names
    for key in ["itinerary", "itinerary_text", "body", "content", "email_content", "html_content", "plan"]:
        if key in args and isinstance(args[key], str) and len(args[key]) > 0:
            return args[key]
    # Fallback to any substantial string argument that is not an email
    for val in args.values():
        if isinstance(val, str) and "@" not in val and len(val) > 40:
            return val
    return ""

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User prompt handling
if prompt := st.chat_input("Plan a trip to..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    try:
        events = graph.stream(
            {"messages": [HumanMessage(content=prompt)]}, 
            thread_config, 
            stream_mode="values"
        )
        
        for event in events:
            last_message = event["messages"][-1]
            if last_message.type == "ai":
                display_text = extract_text(last_message.content)
                
                if not display_text and getattr(last_message, "tool_calls", None):
                    for tool in last_message.tool_calls:
                        extracted = extract_tool_itinerary(tool)
                        if extracted:
                            display_text = extracted
                            break

                if display_text:
                    with st.chat_message("assistant"):
                        st.markdown(display_text, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": display_text})
                    
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            st.error("Gemini API rate limit reached. Please wait 30 seconds before sending your next request.")
        else:
            st.error(f"Error: {e}")

# Human-in-the-loop control check
current_state = graph.get_state(thread_config)
if current_state.next and current_state.next[0] == "email_node":
    st.warning("Review the itinerary above. Do you want to email this to yourself?")
    if st.button("Approve Email Dispatch"):
        with st.spinner("Dispatching email..."):
            result = graph.invoke(None, thread_config)
            final_msg = result["messages"][-1]
            confirmation = extract_text(final_msg.content)
            if not confirmation:
                confirmation = "Email dispatched successfully! Check your inbox."
            st.session_state.messages.append({"role": "assistant", "content": confirmation})
            st.rerun()