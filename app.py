import streamlit as st
from workflow.research_graph import build_research_graph

# ---------------------------------------------------------
# Page Configuration & Metadata
# ---------------------------------------------------------
st.set_page_config(
    page_title="Obsidian AI Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State to prevent output loss on UI reruns
if "final_markdown" not in st.session_state:
    st.session_state.final_markdown = ""
if "research_topic" not in st.session_state:
    st.session_state.research_topic = ""

# ---------------------------------------------------------
# Modern Dark/Glassmorphism CSS Injection
# ---------------------------------------------------------
st.markdown("""
<style>
    :root {
        --bg-main: #0B0E14;
        --card-bg: rgba(22, 27, 38, 0.75);
        --card-border: rgba(255, 255, 255, 0.08);
        --accent-purple: #A78BFA;
        --accent-indigo: #6366F1;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #A78BFA 0%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.05rem;
        margin-bottom: 1.8rem;
        font-weight: 400;
    }

    .agent-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 1.1rem;
        margin-bottom: 0.85rem;
        backdrop-filter: blur(12px);
        transition: all 0.2s ease-in-out;
    }

    .agent-card:hover {
        border-color: rgba(167, 139, 250, 0.4);
        transform: translateY(-2px);
    }

    .agent-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .agent-desc {
        color: var(--text-secondary);
        font-size: 0.82rem;
        margin-top: 0.35rem;
        line-height: 1.4;
    }

    div.stDownloadButton > button {
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.25rem !important;
        box-shadow: 0 4px 14px rgba(139, 92, 246, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }

    div.stDownloadButton > button:hover {
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5) !important;
        transform: translateY(-1px);
    }

    .stCode {
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Credentials, Model Settings & Agent Pipeline
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Model Settings")
    
    # Dynamic Temperature Slider
    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Lower values (0.0 - 0.3) are precise. Higher values (0.7 - 1.0) encourage creative outputs."
    )

    st.markdown("## 🔑 Credentials")
    openai_api_key = st.text_input(
        "OpenAI API Key (Optional)",
        type="password",
        help="Leave blank to run locally via Ollama."
    )

    if not openai_api_key:
        st.info("💡 **Provider:** Local Ollama (`gemma3:4b` / `qwen3:8b`)")
    else:
        st.success("⚡ **Provider:** OpenAI Cloud API")

    tavily_api_key = st.text_input(
        "Tavily API Key (Optional)",
        type="password",
        help="Optional search key. System falls back to DuckDuckGo if omitted."
    )

    st.markdown("---")
    st.markdown("### ⚙️ Multi-Agent Architecture")

    st.markdown("""
    <div class="agent-card">
        <div class="agent-title">🌐 1. Researcher Node</div>
        <div class="agent-desc">Autonomously performs web searches and compiles raw context.</div>
    </div>
    <div class="agent-card">
        <div class="agent-title">🧠 2. Synthesizer Node</div>
        <div class="agent-desc">Distills data, resolves contradictions, and structures technical findings.</div>
    </div>
    <div class="agent-card">
        <div class="agent-title">📝 3. Formatter Node</div>
        <div class="agent-desc">Applies standard YAML frontmatter, [[WikiLinks]], and reference blocks.</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Hero Section & Input Controls
# ---------------------------------------------------------
st.markdown('<div class="hero-title">🧠 Obsidian AI Research Hub</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Autonomous multi-agent pipeline generating Obsidian-native markdown knowledge graphs.</div>',
    unsafe_allow_html=True
)

col_input, col_btn = st.columns([3, 1], vertical_alignment="bottom")

with col_input:
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g., Vector Databases vs Relational Databases in 2026",
        label_visibility="visible"
    )

with col_btn:
    start_research = st.button("🚀 Start Research", type="primary", use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# Workflow Trigger & Graph Streaming Execution
# ---------------------------------------------------------
if start_research:
    if not topic.strip():
        st.warning("⚠️ Please specify a research topic.")
    else:
        st.session_state.research_topic = topic.strip()
        
        # Build initial graph state
        initial_state = {
            "topic": topic.strip(),
            "openai_api_key": openai_api_key.strip() if openai_api_key else "",
            "tavily_api_key": tavily_api_key.strip() if tavily_api_key else "",
            "temperature": temperature,
            "search_results": [],
            "synthesis": "",
            "obsidian_md": ""
        }

        status_box = st.status("⚡ Executing Multi-Agent Pipeline...", expanded=True)

        try:
            # Build compiled LangGraph workflow
            graph = build_research_graph()

            # Stream execution step-by-step through graph nodes
            for step in graph.stream(initial_state):
                for node_name, state_update in step.items():
                    if node_name == "researcher":
                        status_box.write("🌐 **Researcher Agent:** Gathered and summarized web research.")
                    elif node_name == "synthesis":
                        status_box.write("🧠 **Synthesizer Agent:** Analysis and technical synthesis complete.")
                    elif node_name == "obsidian":
                        status_box.write("📝 **Formatter Agent:** Generated YAML frontmatter & [[WikiLinks]].")
                        st.session_state.final_markdown = state_update.get("obsidian_md", "")

            status_box.update(label="✨ Pipeline Execution Complete!", state="complete", expanded=False)

        except Exception as e:
            status_box.update(label="❌ Pipeline Execution Failed", state="error", expanded=True)
            st.error(f"Error during execution: {str(e)}")

# ---------------------------------------------------------
# Output Display & Download Options
# ---------------------------------------------------------
if st.session_state.final_markdown:
    st.markdown("### 📄 Generated Obsidian Note")

    action_col1, action_col2 = st.columns([3, 1], vertical_alignment="center")

    with action_col1:
        st.info("💡 Note complete with YAML frontmatter, `[[WikiLinks]]`, and Markdown references.")

    with action_col2:
        clean_topic = st.session_state.research_topic or "research_note"
        filename = "".join(c for c in clean_topic if c.isalnum() or c in (" ", "_", "-")).rstrip().replace(" ", "_")
        
        st.download_button(
            label="📥 Download .md Note",
            data=st.session_state.final_markdown,
            file_name=f"{filename}.md",
            mime="text/markdown",
            use_container_width=True
        )

    tab_preview, tab_raw = st.tabs(["👁️ Rendered Preview", "💻 Raw Markdown"])

    with tab_preview:
        st.markdown(st.session_state.final_markdown)

    with tab_raw:
        st.code(st.session_state.final_markdown, language="markdown")