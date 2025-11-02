import streamlit as st
import subprocess
import os
import tempfile
import shutil
from dotenv import load_dotenv
import sys
import re

# ✅ Try importing AI dependencies with graceful error handling
try:
    from langchain_google_genai import ChatGoogleGenerativeAI as GeminiAI
    from langchain.agents import initialize_agent, AgentType
    from langchain.memory import ConversationBufferMemory
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain_core.tools import tool
except Exception as e:
    msg = (
        "🚨 Missing required packages for AI features (langchain and related modules).\n\n"
        "👉 Install them using:\n"
        "   pip install langchain langchain-google-genai langchain-community python-dotenv tavily-python\n\n"
        f"Import error details: {e}"
    )
    try:
        st.error(msg)
    except Exception:
        pass
    print(msg)
    sys.exit(1)

# ✅ Load environment variables
load_dotenv()

# ✅ Retrieve API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GEMINI_API_KEY or not TAVILY_API_KEY:
    st.error("Missing API keys. Please set GEMINI_API_KEY and TAVILY_API_KEY in your .env file.")
    st.stop()

# ✅ Define custom tools
@tool
def create_folder(folder_name: str):
    """Create a folder with the given name."""
    try:
        os.makedirs(folder_name, exist_ok=True)
        return f"📁 Folder '{folder_name}' created successfully."
    except Exception as e:
        return f"❌ Error: {str(e)}"

@tool
def create_file(file_name: str, content: str = ""):
    """Create a file with the given name and optional content."""
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        return f"📝 File '{file_name}' created successfully."
    except Exception as e:
        return f"❌ Error: {str(e)}"

@tool
def add_code_to_file(file_name: str, code: str):
    """Add code to the given file."""
    try:
        # Check if file exists and has content
        needs_newline = os.path.exists(file_name) and os.path.getsize(file_name) > 0
        with open(file_name, "a", encoding="utf-8") as f:
            if needs_newline:
                f.write("\n")
            f.write(code)
        return f"✅ Code added to '{file_name}' successfully."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ✅ Streamlit UI
st.set_page_config(page_title="AI-Powered Code Editor", page_icon="💡", layout="wide")

# ✅ Initialize tools and agent (using session state to avoid recreating on each rerun)
if "agent_initialized" not in st.session_state:
    try:
        # ✅ Tavily Search Tool
        tavily_search = TavilySearchResults(api_key=TAVILY_API_KEY)
        
        # ✅ Tools list - @tool decorator already creates Tool objects, use them directly
        tools = [
            create_folder,
            create_file,
            add_code_to_file,
            tavily_search
        ]
        
        # ✅ Initialize AI Agent
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        llm = GeminiAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)
        st.session_state.agent = initialize_agent(
            tools, llm, 
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
            memory=memory, 
            verbose=False
        )
        st.session_state.agent_initialized = True
    except Exception as e:
        st.error(f"Failed to initialize AI agent: {str(e)}")
        st.session_state.agent = None
        st.session_state.agent_initialized = True
st.title("💡 AI-Powered Code Editor")
st.write("Write, execute, and manage your code with AI assistance!")

# ✅ Language selection
language = st.selectbox("Choose Language:", ["Python", "JavaScript", "Java", "C++"])
code = st.text_area("✏️ Write your code here:", height=250, placeholder="Enter your code...")

# ✅ Run Code
if st.button("🚀 Run Code"):
    if code.strip() == "":
        st.error("Please enter some code to run!")
    else:
        with st.spinner("Running your code..."):
            temp_file_path = None
            temp_dir = None
            exe_path = None
            try:
                if language == "Python":
                    suffix = ".py"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="w", encoding="utf-8") as temp_file:
                        temp_file.write(code)
                        temp_file.flush()
                        temp_file_path = temp_file.name
                    result = subprocess.run(["python", temp_file_path], capture_output=True, text=True)

                elif language == "JavaScript":
                    suffix = ".js"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="w", encoding="utf-8") as temp_file:
                        temp_file.write(code)
                        temp_file.flush()
                        temp_file_path = temp_file.name
                    result = subprocess.run(["node", temp_file_path], capture_output=True, text=True)

                elif language == "Java":
                    # Extract public class name
                    match = re.search(r'public\s+class\s+(\w+)', code)
                    if not match:
                        st.error("⚠️ Could not find a public class in your Java code. Please define a public class.")
                        st.stop()
                    class_name = match.group(1)
                    temp_dir = tempfile.mkdtemp()
                    java_file_path = os.path.join(temp_dir, f"{class_name}.java")
                    with open(java_file_path, "w", encoding="utf-8") as f:
                        f.write(code)
                    # Compile
                    compile_result = subprocess.run(["javac", java_file_path], capture_output=True, text=True)
                    if compile_result.stderr:
                        st.subheader("⚠️ Compilation Errors:")
                        st.code(compile_result.stderr.strip(), language="bash")
                        result = None
                    else:
                        # Run
                        result = subprocess.run(["java", "-cp", temp_dir, class_name], capture_output=True, text=True)

                elif language == "C++":
                    suffix = ".cpp"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="w", encoding="utf-8") as temp_file:
                        temp_file.write(code)
                        temp_file.flush()
                        temp_file_path = temp_file.name
                    # Create executable with proper name
                    exe_path = temp_file_path.rsplit('.', 1)[0] + ".exe" if os.name == 'nt' else temp_file_path.rsplit('.', 1)[0]
                    compile_result = subprocess.run(["g++", temp_file_path, "-o", exe_path], capture_output=True, text=True)
                    if compile_result.stderr:
                        st.subheader("⚠️ Compilation Errors:")
                        st.code(compile_result.stderr.strip(), language="bash")
                        result = None
                    else:
                        result = subprocess.run([exe_path], capture_output=True, text=True)

                else:
                    st.error("Unsupported language!")
                    st.stop()

                if result:
                    st.success("Execution Complete ✅")
                    if result.stdout.strip():
                        st.subheader("🖥️ Output:")
                        st.code(result.stdout.strip(), language="bash")
                    if result.stderr.strip():
                        st.subheader("⚠️ Errors:")
                        st.code(result.stderr.strip(), language="bash")

            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                # Clean up temporary files
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except Exception:
                        pass
                if exe_path and os.path.exists(exe_path):
                    try:
                        os.unlink(exe_path)
                    except Exception:
                        pass
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass
