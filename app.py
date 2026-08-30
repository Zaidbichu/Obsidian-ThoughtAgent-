import os
import streamlit as st
from workflow.research_graph import build_research_graph

# Page Configuration
st.set_page_config(
    page_title="Obsidian Research Agent",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Autonomous Obsidian Research Agent")
st.caption("Multi-Agent Graph for Web Research and Obsidian Vault Note Generation")

# ---------------------------------------------------------
# Sidebar: Provider & Configuration Settings
# ---------------------------------------------------------
st.sidebar.title("⚙️ LLM & Search Settings")

provider = st.sidebar.selectbox(
    "Choose LLM Provider",
    options=["OpenAI", "Ollama (Local Only)"],
    index=0,
    help="Select OpenAI for cloud deployment, or Ollama for local execution."
)

api_key = ""
model_name = ""

if provider == "OpenAI":
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key (starts with 'sk-'). Required on Streamlit Cloud."
    )
    
    model_name = st.sidebar.selectbox(
        "Select OpenAI Model",
        options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
        index=0
    )
    
    if not api_key and not os.getenv("OPENAI_API_KEY"):
        st.sidebar.warning("⚠️ Please provide an OpenAI API key to execute research.")

else:
    model_name = st.sidebar.text_input(
        "Ollama Model Name",
        value="llama3",
        help="Model string running on http://localhost:11434"
    )
    st.sidebar.info("💡 Local Ollama execution requires Ollama to be running on your machine.")

st.sidebar.markdown("---")
tavily_key = st.sidebar.text_input(
    "Tavily API Key (Optional)",
    type="password",
    help="If provided, the agent will use Tavily Search. Otherwise, it falls back to DuckDuckGo."
)

# ---------------------------------------------------------
# Main Execution Interface
# ---------------------------------------------------------
query = st.text_input(
    "Research Topic",
    placeholder="e.g., Quantum Computing Applications in Logistics"
)

if st.button("🚀 Start Research Workflow", type="primary"):
    selected_provider = "openai" if provider == "OpenAI" else "ollama"
    
    if selected_provider == "openai" and not api_key and not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OpenAI API Key is missing. Please enter it in the sidebar.")
    elif not query.strip():
        st.warning("⚠️ Please enter a research topic.")
    else:
        # 1. Package runtime config dictionary for agent nodes
        config = {
            "provider": selected_provider,
            "model_name": model_name,
            "api_key": api_key,
            "tavily_key": tavily_key
        }
        
        # 2. Setup initial graph state
        initial_state = {
            "query": query,
            "config": config,
            "research_data": "",
            "synthesized_text": "",
            "final_output": ""
        }
        
        # 3. Build state graph
        app_graph = build_research_graph()
        
        # 4. Stream status updates during node transitions
        status_box = st.status("🔍 Initializing agent graph workflow...", expanded=True)
        final_markdown = ""
        
        try:
            for event in app_graph.stream(initial_state):
                for node_name, state_update in event.items():
                    if node_name == "researcher":
                        status_box.write("🌐 **Researcher Agent:** Web search completed and facts extracted.")
                        
                    elif node_name == "synthesizer":
                        status_box.write("⚙️ **Synthesizer Agent:** Key insights and mechanics distilled.")
                        
                    elif node_name == "formatter":
                        status_box.write("📝 **Obsidian Formatter:** Frontmatter, headers, and [[WikiLinks]] applied.")
                        final_markdown = state_update.get("final_output", "")
            
            status_box.update(label="✅ Workflow Execution Complete!", state="complete", expanded=False)

        except Exception as err:
            status_box.update(label="❌ Error during workflow execution", state="error", expanded=True)
            st.error(f"Execution Error: {str(err)}")

        # 5. Output rendering and file download
        if final_markdown:
            st.subheader("📄 Generated Obsidian Note")
            st.markdown(final_markdown)
            
            st.markdown("---")
            st.subheader("🛠️ Raw Markdown Source")
            st.code(final_markdown, language="markdown")
            
            filename = f"{query.replace(' ', '_').lower()}_note.md"
            st.download_button(
                label="📥 Download Markdown File",
                data=final_markdown,
                file_name=filename,
                mime="text/markdown"
            )
