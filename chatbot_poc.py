import streamlit as st
from groq import Groq

# Page configuration
# st.set_page_config(page_title="Databricks FinOps Advisor", page_icon="💼", layout="centered")
st.set_page_config(page_title="Databricks FinOps Advisor", page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTG5dgueFTq1hwBzJiphTA4QWNFTNWiPM4qTw&s", layout="centered")

# Title
# st.title("💼 Databricks FinOps Advisor")
st.set_page_config(layout="wide")

# System Prompt
SYSTEM_PROMPT = """You are a Databricks FinOps Advisor AI assistant. Your role is to help users who have little to no knowledge about Databricks plan their migration from their current data platform to Databricks. You will collect information conversationally, then provide migration recommendations, architecture design, and cost estimates.

## YOUR OBJECTIVES:
1. Collect required information through natural conversation
2. Create structured entity mapping from user responses
3. Recommend migration plan and Databricks architecture
4. Provide cost estimation guidance

## CONVERSATION GUIDELINES:
- Use simple, jargon-free language - users are new to Databricks
- Ask questions naturally, 1 at a time (don't overwhelm)
- Be conversational and friendly
- Listen carefully and adapt follow-up questions based on answers
- Allow users to skip questions - if they do, make reasonable assumptions and explain them
- If user provides unclear answers, ask clarifying questions
- Never invent technical details, pricing, or features

## MANDATORY INFORMATION TO COLLECT (Priority):
You MUST collect these 8 pieces of information before making recommendations:

1. **Current Data Platform/Technology**
   - What is their current data platform? (e.g., on-premises databases, cloud data warehouse, Hadoop, other)
   - Which specific technologies? (e.g., SQL Server, Oracle, PostgreSQL, Snowflake, Redshift, Teradata, Hadoop/Spark)

2. **Total Data Volume**
   - How much data do they have? (in GB or TB or PB)

3. **Primary Use Cases/Workload Types**
   - What do they use data for? (ETL/ELT pipelines, reporting, analytics, data science/ML, real-time streaming)

4. **Data Ingestion Rate**
   - How much data do they ingest daily or monthly?

5. **Batch Job Frequency & Count**
   - How many batch jobs do they run? (daily/weekly)
   - What are their batch processing windows? (e.g., overnight, 4-hour windows)

6. **Concurrent Users/Query Load**
   - How many users query the system concurrently?

7. **Cloud Provider Preference**
   - Which cloud provider do they prefer? (Azure, AWS, or flexible)

8. **Data Location**
   - Where is their data currently stored? (on-premises, Azure region, AWS region, GCP, multi-cloud)

## OPTIONAL INFORMATION (Collect if possible):
- Industry
- Organization size
- Data types (structured, semi-structured, unstructured)
- Data model details (number of raw tables, transformed tables, final models)
- Real-time/streaming requirements
- Peak usage times
- Data freshness requirements (real-time, hourly, daily)
- Compliance requirements (GDPR, HIPAA, SOC2, PCI-DSS, etc.)
- BI/reporting tools (Power BI, Tableau, Looker, etc.)
- Orchestration tools (Airflow, Azure Data Factory, AWS Step Functions, etc.)
- Current infrastructure costs
- Team size and skill level
- Migration timeline preferences
- Pain points with current system

## HANDLING SKIPPED QUESTIONS:
If a user skips a mandatory question:
1. Acknowledge their choice
2. Make a reasonable assumption based on context
3. Clearly state: "I'm assuming [assumption]. This means [impact on recommendation]."
4. Note that they can provide this information later to refine recommendations

If a user skips an optional question:
1. Make a reasonable default assumption
2. Briefly mention the assumption without over-explaining

## ENTITY MAPPING:
Once you have collected all mandatory information (or user requests recommendations), create a structured entity mapping in JSON format.

**If user provided optional information (industry, organization_size, pain_points, etc.), use this extended schema:**
```json
{
  "industry": "<if mentioned>",
  "organization_size": "<if mentioned>",
  "databricks_user": "new",
  "current_platform": {
    "data_warehouse": "<technology name>",
    "etl_tool": "<if mentioned>",
    "scheduler": "<if mentioned>",
    "bi_tool": "<if mentioned>"
  },
  "data_volume": {
    "warehouse_size_tb": <number>,
    "daily_ingest_tb": <number>,
    "batch_window_hours": "<timeframe>"
  },
  "data_model": {
    "raw_tables": <number if mentioned>,
    "transformed_tables": <number if mentioned>,
    "final_models": <number if mentioned>
  },
  "workload_types": ["<list of use cases>"],
  "data_types": ["<if mentioned>"],
  "batch_jobs": {
    "daily_count": <number>,
    "weekly_count": <number>
  },
  "concurrent_users": <number>,
  "cloud_provider": "<Azure|AWS|Flexible>",
  "data_location": "<on-prem|region>",
  "streaming_required": <boolean>,
  "compliance_requirements": ["<if mentioned>"],
  "current_cost_usd": <number if mentioned>,
  "pain_points": ["<if mentioned>"],
  "assumptions": [
    "<list any assumptions made for skipped questions>"
  ]
}
```

**If user only provided mandatory information, use this simplified schema:**
```json
{
  "current_platform": {
    "data_warehouse": "<technology name>",
    "etl_tool": "<if mentioned>",
    "scheduler": "<if mentioned>",
    "bi_tool": "<if mentioned>"
  },
  "data_volume": {
    "warehouse_size_tb": <number>,
    "daily_ingest_tb": <number>,
    "batch_window_hours": "<timeframe>"
  },
  "workload_types": ["<list of use cases>"],
  "batch_jobs": {
    "daily_count": <number>,
    "weekly_count": <number>
  },
  "concurrent_users": <number>,
  "cloud_provider": "<Azure|AWS|Flexible>",
  "data_location": "<on-prem|region>",
  "assumptions": [
    "<list any assumptions made for skipped questions>"
  ]
}
```

Present this entity mapping to the user and ask: "Here's what I've understood about your environment. Does this look correct? Would you like to modify anything before I provide recommendations?"

## AFTER ENTITY MAPPING CONFIRMATION:
Once the entity mapping is confirmed, provide:

1. **Detailed Migration Plan with Phases**: Break down the migration into clear phases (e.g., Phase 1: Assessment & Setup, Phase 2: Data Migration, Phase 3: Workload Migration, Phase 4: Optimization). Include timeline estimates for each phase.

2. **Databricks Architecture Recommendations**: Describe the recommended architecture including:
   - Workspace structure
   - Compute resources (cluster types, sizing)
   - Storage strategy
   - Security and governance approach
   - Integration points
   - Best practices for their specific use case

Provide these recommendations in a clear, structured format that a non-technical user can understand.

## IMPORTANT CONSTRAINTS:
- NEVER invent Databricks features, services, or pricing
- NEVER perform cost calculations yourself (those will be done by a separate deterministic system)
- Only recommend Databricks services and features that actually exist
- If you're uncertain about something, ask the user for clarification
- Reference that your recommendations are based on Databricks best practices

## CONVERSATION FLOW:
1. Greet the user warmly and explain you'll help them plan their Databricks migration
2. Start collecting mandatory information conversationally
3. Collect optional information naturally as conversation flows
4. Once mandatory info is collected or user requests recommendations, create entity mapping
5. Confirm entity mapping with user and allow modifications
6. Provide detailed migration plan with phases
7. Provide detailed architecture recommendations
8. Inform user that cost estimation will be calculated separately based on this plan

Remember: You're helping users who are NEW to Databricks. Be patient, educational, and supportive throughout the conversation. Allow users to update their answers and refine recommendations at any point."""


st.markdown("""
<link rel="stylesheet"
href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap">
            
<style>

    /* Full-page background gradient */
    .stApp {
        background: #e9fdfa;
        background-attachment: fixed;
    }

    /* Optional – remove white gaps */
    main {
        background: transparent !important;
    }
                
    /* Hide Streamlit default header (hamburger + Deploy) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0px;
    }

    /* Also remove extra spacing it leaves */
    header[data-testid="stHeader"] * {
        display: none;
    }

    #             /* 1️⃣ Set full-page background everywhere */
    # html, body, .stApp {
    #     # background: linear-gradient(135deg, #1e3a8a, #020617) !important;
    #             background: #abf8ea;
    #     background-attachment: fixed;
    # }

    # /* 2️⃣ Header bar (Streamlit default menu and Deploy button area) */
    # header[data-testid="stHeader"] {
    #     background: linear-gradient(135deg, #1e3a8a, #020617) !important;
    # }

    # /* 3️⃣ Main content container */
    # [data-testid="stAppViewContainer"] {
    #     background: transparent !important;
    # }

    # /* 4️⃣ Sidebar background (match page) */
    # section[data-testid="stSidebar"] {
    #     background: linear-gradient(135deg, #1e3a8a, #020617) !important;
    # }

    /* 5️⃣ Bottom chat input container (white strip issue) */
    [data-testid="stBottomBlockContainer"] {
        # background: linear-gradient(135deg, #1e3a8a, #020617) !important;
                background: #71b6b1;
                width: 100% !important;
        max-width: 100% !important;
        flex-grow: 1 !important;
        flex-shrink: 0 !important;
    }

    #stBottomBlockContainer > div {
        width: 100% !important;
    }
                
    # /* Also style the chat input box background */
    # [data-baseweb="textarea"] > div {
    #     background: rgba(0,0,0,0.3) !important;
    #     color: white !important;
    # }
                
                            
    /* Make the entire app full-width */
    [data-testid="stAppViewContainer"] > .main {
        max-width: 100%;
        padding-left: 0;
        padding-right: 0;
    }

    /* Remove Streamlit default padding and centering */
    .block-container {
        max-width: 100%;
        padding-top: 0;
        padding-left: 0;
        padding-right: 0;
    }

    /* Full-width top navigation bar */
    .top-nav {
        width: 100vw;               /* full viewport width */
        margin-top:50px;
        margin-left: calc(-50vw + 50%); /* stretch beyond centered container */
        # background: #B7D3C8;
        background: linear-gradient(180deg,#71b6b1 0%,#B7D3C8 100% );
        padding: 16px 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 999;
        position: fixed;
    }

    .top-nav .title {
        font-family: "Poppins", sans-serif !important;
        font-size: 22px;
        font-weight: bold;
        color: #1F3D36;
        padding-left: 20px;
    }
                
    .top-nav .menu{
        padding-right: 20px;         
    }

    .top-nav .menu a {
        font-family: "Poppins", sans-serif !important;
        color: #1F3D36;
        margin-left: 18px;
        text-decoration: none;
        padding-right: 20px;
    }

    .top-nav .menu a:hover {
        text-decoration: none;
    }
                
    .header-logo {
        position: fixed;
        width:100%;
        margin: 0 !important;
        height:50px;
        top: 0;
        left: 0;
        z-index: 9999;
        display: flex;
        /*border: 1px solid red;*/
        background: #e9fdfa;
    }  

    .header-logo img{
        padding-top:10px;
        padding-left:50px;
    }        
                
    .two-col-block {
        font-family: "Poppins", sans-serif !important;
        display: flex;
        gap: 50px;
        margin-top: 70px;
        padding: 80px;
        padding-bottom: 40px;
        min-height: 30vh;        /* height of each box */
    }

    .col {
        flex: 1;
        # border: 5px solid red;
        padding: 20px;
        border-radius: 12px;
        background: white;
        box-sizing: border-box;
        box-shadow: rgba(0, 0, 0, 0.1) 1px 1px 0px 0px, rgba(0, 0, 0, 0.1) -1px 1px 0px 0px;
    }            

    .col ol {
        padding-left: 20px;
    }

    .col ol ul {
        margin-top: 6px;
        padding-left: 24px;
        list-style-type: disc;
    }

    .col ol ul li {
        font-size: 0.95rem;
        color: #555;
    }

    .col ul {
        list-style: none;
        padding-left: 0;
        margin-top: 8px;
    }

    .col ul li {
        margin-bottom: 6px;
    }
                
    .section-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
    }

    .title-icon {
        font-size: 1.2em;
    }
                
    /* Make chat input stack vertically instead of side-by-side */
    [data-testid="stChatInput"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        padding-top: 24px !important;     /* space ABOVE chat box  */
        padding-bottom: 24px !important;  /* space BELOW chat box  */
        min-height: 140px !important;     /* overall bar height    */
    }

    /* Title above chat box */
    [data-testid="stChatInput"]::before {
        content: "💬 Start a conversation";
        width: 100%;
        display: block;
        text-align: left;
        margin-bottom: 8px;
        font-size: 18px;
        font-weight: 700;
        color: white;
    }

    /* Nice spacing for the input box itself */
    [data-testid="stChatInput"] > div {
        width: 100%;
        border-radius: 12px;
    }
   
</style>


<div class="header-logo">
    <img src="https://mresult.com/wp-content/uploads/2025/06/Mlogo-e1665656493505-1.png" height="40">
</div>
            
<div class="top-nav">
    <div class="title">Databricks FinOps Advisor</div>
    <div class="menu">
        <a href="#home">Home</a>
        <a href="#features">Features</a>
        <a href="#about">About</a>
    </div>
</div>
            
<div class="two-col-block">

  <div class="col">
    <h3><span class="title-icon">💡</span>What is Databricks FinOps Advisor?</h3>
    <p>
    This advisor helps organizations plan, optimize, and govern costs while
    migrating to Databricks.
    </p>
    <ul>
        <li>🔍 Understand existing workloads</li>
        <li>🧱 Design cost-efficient architectures</li>
        <li>💰 Estimate and control Databricks costs</li>
        <li>📊 Improve cost visibility and accountability</li>
    </ul>
            
  </div>

  <div class="col">
    <h3>🧭 How It Works? </h3>
    <ol>
        <li>Describe your data and workload needs</li>
            <ul>
                <li>Share your current data platform, workloads, and scale.</li>
            </ul>
        <li>Answer guided FinOps questions</li>
            <ul>
                <li>The advisor will ask about data volume, frequency, users, and SLAs.</li>
            </ul>
        <li>Receive architecture & cost recommendations</li>
            <ul>
                <li>Receive recommendations on:   
                    <ul>
                        <li>cluster types</li>
                        <li>job vs all-purpose compute</li>
                        <li>storage & networking</li>
                        <li>cost-saving levers</li>
                    </ul>
                </li>
            </ul>
        <li>Iterate to optimize performance and spend</li>
            <ul>
                <li>Update inputs anytime to see optimized recommendations.</li>
            </ul>
    </ol>
  </div>

</div>
            
""", unsafe_allow_html=True)




# Initialize Groq client
@st.cache_resource
def get_groq_client():
    import os
    api_key = st.secrets.get("GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("⚠️ Please set GROQ_API_KEY environment variable or in Streamlit secrets")
        st.info("Get your API key from: https://console.groq.com")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()


# Initialize chat history with system prompt
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Display chat history (skip system message)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# st.write("Ask a question or describe your use case below:")
if prompt := st.chat_input("Ask a question or describe your use case here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream response from Groq
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                max_tokens=2048,  # Increased for detailed recommendations
                temperature=0.7
            )
            
            # Display streaming response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"Error: {str(e)}"
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# # Sidebar with options
# with st.sidebar:
#     st.header("⚙️ Settings")
    
#     if st.button("🔄 Start New Assessment"):
#         st.session_state.messages = [
#             {"role": "system", "content": SYSTEM_PROMPT}
#         ]
#         st.rerun()
    
#     st.markdown("---")
#     st.markdown("### 📋 About")
#     st.markdown("""
#     This Databricks FinOps Advisor helps you:
#     - Plan your migration to Databricks
#     - Design optimal architecture
#     - Estimate migration costs
    
#     **Perfect for users new to Databricks!**
#     """)
    
#     st.markdown("---")
#     st.markdown("### 💡 Tips")
#     st.markdown("""
#     - Answer questions conversationally
#     - You can skip questions if unsure
#     - Update your answers anytime
#     - Ask for clarification when needed
#     """)
    
#     st.markdown("---")
#     st.markdown("### 🤖 Powered by")
#     st.markdown("Groq API with Llama 3.3 70B")
