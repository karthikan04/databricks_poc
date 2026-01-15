"""Databricks FinOps Advisor with Multi-Domain RAG Integration
Separate knowledge bases for Migration, Optimization, and Costing"""


import streamlit as st
from groq import Groq
import os
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# For RAG
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

# ============================================================================
# CONFIGURATION - SEPARATED DOCUMENTATION URLS BY DOMAIN
# ============================================================================

MIGRATION_URLS = [
	"https://www.databricks.com/blog/migrating-redshift-databricks-field-guide-data-teams#:~:text=and%20cost%20visibility.-,Pre%2Dmigration%20steps,with%20your%20goals%20and%20timelines.",
	"https://www.databricks.com/blog/navigating-your-migration-databricks-architectures-and-strategic-approaches",
	"https://www.databricks.com/blog/databricks-migration-strategy-lessons-learned",
	"https://www.databricks.com/blog/how-databricks-simplifies-data-warehouse-migrations-proven-strategies-and-tools",
	"https://www.databricks.com/blog/2022/06/24/data-warehousing-modeling-techniques-and-their-implementation-on-the-databricks-lakehouse-platform.html",
	"https://www.databricks.com/blog/how-migrate-your-oracle-plsql-code-databricks-lakehouse-platform",
	"https://www.databricks.com/blog/navigating-oracle-databricks-migration-tips-seamless-transition",
	"https://www.databricks.com/sites/default/files/2025-05/databricks-migration-guide-oracle-fa.pdf",
	"https://www.databricks.com/sites/default/files/2025-05/databricks-migration-guide-microsoft-sql-fa.pdf",
	"https://www.databricks.com/blog/navigating-your-netezza-databricks-migration-tips-seamless-transition",
	"https://www.databricks.com/blog/best-practices-and-guidance-cloud-engineers-deploy-databricks-aws-part-3",
	"https://www.databricks.com/blog/introducing-lakebridge-free-open-data-migration-databricks-sql",
	"https://www.databricks.com/blog/warehouse-lakehouse-migration-approaches-databricks",
	"https://www.devoteam.com/expert-view/data-warehouse-migration-to-databricks-a-comprehensive-guide/",
	"https://closeloop.com/blog/how-to-migrate-to-databricks-best-practices/",
	"https://www.datafold.com/resources/hadoop-to-databricks-migration",
	"https://kanerika.com/blogs/legacy-systems-to-databricks-migration/",
	"https://www.msrcosmos.com/blog/databricks-data-migration-steps-and-benefits/",
	"https://www.striim.com/blog/oracle-data-databricks-unity-catalog-python-and-databricks-notebook-recipe/",
	"https://www.sparity.com/blogs/snowflake-to-databricks-migration/",
	"https://blog.aidetic.in/migrating-from-bigquery-to-databricks-a-step-by-step-practical-guide-c7d8e18efaf3"
]

ARCHITECTURE_URLS = [
	"https://www.databricks.com/blog/navigating-your-migration-databricks-architectures-and-strategic-approaches",
	"https://www.databricks.com/blog/2023/03/30/security-best-practices-databricks-lakehouse-platform.html",
	"https://www.databricks.com/blog/2023/03/30/security-best-practices-databricks-lakehouse-platform.html",
	"https://www.databricks.com/blog/best-practices-and-guidance-cloud-engineers-deploy-databricks-aws-part-2",
	"https://www.databricks.com/blog/best-practices-and-guidance-cloud-engineers-deploy-databricks-aws-part-3",
	"https://www.databricks.com/blog/data-architecture-pattern-maximize-value-lakehouse.html",
	"https://docs.databricks.com/aws/en/getting-started/high-level-architecture#classic-workspace-architecture",
	"https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-databricks",
	"https://docs.databricks.com/en/getting-started/overview.html",
	"https://docs.databricks.com/en/lakehouse-architecture/index.html",
	"https://docs.gcp.databricks.com/lakehouse-architecture/index.html",
	"https://learn.microsoft.com/en-us/azure/databricks/getting-started/overview",
	"https://www.bluetab.net/en/databricks-on-aws-an-architectural-perspective-part-1/",
	"https://www.databricks.com/trust/architecture",
	"https://docs.databricks.com/en/security/index.html",
	"https://www.databricks.com/blog/2020/05/04/azure-databricks-security-best-practices.html",
	"https://docs.databricks.com/en/lakehouse-architecture/security-compliance-and-privacy/index.html",
	"https://medium.com/@accentfuture/databricks-architecture-overview-components-workflow-ee00c965a445",
	"https://www.databricks.com/resources/architectures/data-ingestion-reference-architecture",
	"https://gem-corp.tech/tech-blogs/databricks-architecture/",
	"https://www.databricks.com/resources/architectures/reference-architecture-for-security-lakehouse",
	"https://docs.databricks.com/aws/en/compute/choose-compute",
	"https://sanjeebiitg.medium.com/databricks-part-04-understanding-databrick-compute-19d8d81a03e9",
	"https://docs.databricks.com/aws/en/compute/cluster-config-best-practices",
	"https://learn.microsoft.com/en-us/azure/databricks/compute/choose-compute",
	"https://www.unraveldata.com/resources/databricks-serverless-vs-classic-compute/",
	"https://blog.devgenius.io/databricks-compute-selection-6d921a08ead8",
	"https://www.sunnydata.ai/blog/7rbdn3spyh9pjjwty3ca7303xkqeq1",
	"https://docs.databricks.com/aws/en/compute/standard-limitations",
	"https://www.cloudformations.org/post/navigating-databricks-compute-options-for-cost-effective-and-high-performance-solutions",
	"https://medium.com/@krthiak/choosing-cluster-configuration-in-databricks-day-81-of-100-days-of-data-engineering-ai-and-azure-322cda50fc97",
	"https://learn.microsoft.com/en-us/training/wwl-databricks/select-and-configure-compute/2-choose-appropriate-compute-type"
]

COSTING_URLS = [
    "https://www.databricks.com/product/pricing",
    "https://www.databricks.com/product/aws-pricing",
    "https://www.databricks.com/product/azure-pricing",
    "https://docs.databricks.com/en/administration-guide/account-settings-e2/pricing.html",
    "https://docs.databricks.com/en/compute/configure.html",  # DBU consumption
    "https://docs.databricks.com/en/optimizations/cost-optimization.html",
    # Add more costing-related URLs
]

# Keywords to identify which knowledge base to use
MIGRATION_KEYWORDS = [
    "migrate", "migration", "move", "transfer", "from", "current platform",
    "legacy", "modernize", "onboard", "transition", "switch"
]

ARCHITECTURE_KEYWORDS = [
    "optimize", "optimization", "performance", "speed", "faster", "improve",
    "efficiency", "tuning", "autoscaling", "photon", "best practice", "architecture", "compute"
]

COSTING_KEYWORDS = [
    "cost", "price", "pricing", "expensive", "budget", "spend", "billing",
    "dbu", "tier", "savings", "reduce cost", "estimate", "fee"
]

# ============================================================================
# RAG SYSTEM CLASS
# ============================================================================

class DatabricksKnowledgeBase:
    """
    RAG system with separate knowledge bases for different domains
    """
    
    def __init__(self, base_directory: str = "./knowledge_bases"):
        self.base_directory = base_directory
        self.embeddings = None
        
        # Separate vector stores for each domain
        self.migration_vectorstore = None
        self.architecture_vectorstore = None
        self.costing_vectorstore = None
        
        # Track initialization status
        self.initialized = False
    
    def _get_embeddings(self):
        """Get or create embeddings model (cached)"""
        if 'embeddings' not in st.session_state:
            st.session_state.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        return st.session_state.embeddings
    
    def initialize(self):
        """Initialize all knowledge bases"""
        self.embeddings = self._get_embeddings()
        
        # Define paths for each knowledge base
        migration_path = os.path.join(self.base_directory, "migration")
        architecture_path = os.path.join(self.base_directory, "architecture")
        costing_path = os.path.join(self.base_directory, "costing")
        
        # Check if all knowledge bases exist
        all_exist = (
            os.path.exists(migration_path) and
            os.path.exists(architecture_path) and
            os.path.exists(costing_path)
        )
        
        if not all_exist:
            return False  # Need to build
        
        # Load existing vector stores
        try:
            self.migration_vectorstore = Chroma(
                persist_directory=migration_path,
                embedding_function=self.embeddings,
                collection_name="migration"
            )
            
            self.architecture_vectorstore = Chroma(
                persist_directory=architecture_path,
                embedding_function=self.embeddings,
                collection_name="architecture"
            )
            
            self.costing_vectorstore = Chroma(
                persist_directory=costing_path,
                embedding_function=self.embeddings,
                collection_name="costing"
            )
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Error loading knowledge bases: {e}")
            return False
    
    def fetch_webpage(self, url: str) -> str:
        """Fetch and clean webpage content"""
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""
    
    def _build_single_kb(self, urls: List[str], domain: str, persist_path: str, 
                         status_text=None) -> tuple:
        """Build a single knowledge base for a specific domain"""
        documents = []
        
        for idx, url in enumerate(urls):
            if status_text:
                status_text.text(f"Loading {domain} documentation: {idx+1}/{len(urls)}")
            
            content = self.fetch_webpage(url)
            
            if content:
                doc = Document(
                    page_content=content,
                    metadata={"source": url, "domain": domain}
                )
                documents.append(doc)
        
        if status_text:
            status_text.text(f"Processing {domain} documentation...")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        splits = text_splitter.split_documents(documents)
        
        if status_text:
            status_text.text(f"Indexing {domain} content ({len(splits)} chunks)...")
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=persist_path,
            collection_name=domain
        )
        
        vectorstore.persist()
        
        return len(splits), len(documents)
    
    def build_all_knowledge_bases(self):
        """Build all three knowledge bases"""
        os.makedirs(self.base_directory, exist_ok=True)
        
        migration_path = os.path.join(self.base_directory, "migration")
        architecture_path = os.path.join(self.base_directory, "optimization")
        costing_path = os.path.join(self.base_directory, "costing")
        
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        # Build Migration KB
        status_text.text("Building Migration knowledge base...")
        m_chunks, m_docs = self._build_single_kb(
            MIGRATION_URLS, "migration", migration_path, status_text
        )
        progress_bar.progress(0.33)
        
        # Build architeture KB
        status_text.text("Building Architecture knowledge base...")
        o_chunks, o_docs = self._build_single_kb(
            ARCHITECTURE_URLS, "architecture", architecture_path, status_text
        )
        progress_bar.progress(0.66)
        
        # Build Costing KB
        status_text.text("Building Costing knowledge base...")
        c_chunks, c_docs = self._build_single_kb(
            COSTING_URLS, "costing", costing_path, status_text
        )
        progress_bar.progress(1.0)
        
        # Clean up
        status_text.empty()
        progress_bar.empty()
        
        # Load the created vector stores
        self.initialize()
        
        return {
            "migration": {"chunks": m_chunks, "docs": m_docs},
            "architecture": {"chunks": o_chunks, "docs": o_docs},
            "costing": {"chunks": c_chunks, "docs": c_docs}
        }
    
    def _detect_domain(self, query: str) -> str:
        """
        Detect which domain the query belongs to
        Returns: 'migration', 'architecture', 'costing', or 'all'
        """
        query_lower = query.lower()
        
        # Count keyword matches for each domain
        migration_score = sum(1 for kw in MIGRATION_KEYWORDS if kw in query_lower)
        architecture_score = sum(1 for kw in ARCHITECTURE_KEYWORDS if kw in query_lower)
        costing_score = sum(1 for kw in COSTING_KEYWORDS if kw in query_lower)
        
        # If multiple domains match, return 'all'
        matches = []
        if migration_score > 0:
            matches.append(('migration', migration_score))
        if architecture_score > 0:
            matches.append(('architecture', architecture_score))
        if costing_score > 0:
            matches.append(('costing', costing_score))
        
        if len(matches) == 0:
            # No specific keywords, search all
            return 'all'
        elif len(matches) == 1:
            return matches[0][0]
        else:
            # Return domain with highest score
            return max(matches, key=lambda x: x[1])[0]
    
    def get_relevant_context(self, query: str, k: int = 3, domain: Optional[str] = None) -> str:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            k: Number of chunks to retrieve per domain
            domain: Specific domain to search ('migration', 'architecture', 'costing', or None for auto-detect)
        
        Returns:
            Formatted context string
        """
        if not self.initialized:
            return ""
        
        # Auto-detect domain if not specified
        if domain is None:
            domain = self._detect_domain(query)
        
        results = []
        
        try:
            # Search based on detected/specified domain
            if domain == 'migration' and self.migration_vectorstore:
                results = self.migration_vectorstore.similarity_search(query, k=k)
            
            elif domain == 'architecture' and self.architecture_vectorstore:
                results = self.architecture_vectorstore.similarity_search(query, k=k)
            
            elif domain == 'costing' and self.costing_vectorstore:
                results = self.costing_vectorstore.similarity_search(query, k=k)
            
            elif domain == 'all':
                # Search all domains (fewer results per domain)
                per_domain_k = max(1, k // 3)
                
                if self.migration_vectorstore:
                    results.extend(
                        self.migration_vectorstore.similarity_search(query, k=per_domain_k)
                    )
                
                if self.architecture_vectorstore:
                    results.extend(
                        self.architecture_vectorstore.similarity_search(query, k=per_domain_k)
                    )
                
                if self.costing_vectorstore:
                    results.extend(
                        self.costing_vectorstore.similarity_search(query, k=per_domain_k)
                    )
            
            if not results:
                return ""
            
            # Format results
            context_parts = []
            for i, doc in enumerate(results, 1):
                source_url = doc.metadata.get('source', 'Unknown')
                doc_domain = doc.metadata.get('domain', 'unknown')
                
                # Shorten URL for readability
                source_display = source_url.split('/')[-1] if '/' in source_url else source_url
                
                context_parts.append(
                    f"[{doc_domain.upper()} - Reference {i}: {source_display}]\n{doc.page_content}"
                )
            
            return "\n\n---\n\n".join(context_parts)
        
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return ""

# ============================================================================
# INITIALIZE KNOWLEDGE BASES ON APP STARTUP
# ============================================================================

@st.cache_resource(show_spinner=False)
def initialize_knowledge_bases():
    """
    Initialize and load all knowledge bases
    This runs once when the app starts
    """
    kb = DatabricksKnowledgeBase()
    
    # Try to load existing knowledge bases
    loaded = kb.initialize()
    
    if not loaded:
        try:
            kb.build_all_knowledge_bases()
        except Exception as e:
            pass  # Silent failureo("The chatbot will continue without documentation support.")
    
    return kb

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Databricks FinOps Advisor",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTG5dgueFTq1hwBzJiphTA4QWNFTNWiPM4qTw&s",
    layout="centered",
    initial_sidebar_state="collapsed"
)
 
# Title
st.set_page_config(layout="wide")

# ============================================================================
# SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT = """You are a Databricks FinOps Advisor AI assistant. Your role is to help users who have little to no knowledge about Databricks plan their migration from their current data platform to Databricks. You will collect information conversationally, then provide migration recommendations, architecture design, and cost estimates.

## IMPORTANT: You have access to specialized Databricks documentation across three domains:
1. **Migration**: Documentation about migrating from various platforms to Databricks
2. **Architecture**: Documentation about architecture recommendataion, performance tuning, cluster optimization, and best practices
3. **Costing**: Documentation about pricing, DBU consumption, and cost optimization

When answering questions, you will be provided with relevant documentation from the appropriate domain(s). Use this context to give accurate, up-to-date information. When you use information from the documentation, you can mention the domain naturally (e.g., "According to Databricks migration documentation..." or "Based on optimization best practices...").

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
- Never invent technical details, pricing, or features - use the provided documentation context

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

Do not present this entity mapping to the user and ask: "Here's what I've understood about your environment. Does this look correct? Would you like to modify anything before I provide recommendations?"

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
- Reference that your recommendations are based on Databricks best practices and documentation

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

# ============================================================================
# Homepage Design
# ============================================================================
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

# ============================================================================
# INITIALIZE COMPONENTS
# ============================================================================

@st.cache_resource
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("⚠️ Please set GROQ_API_KEY environment variable or in Streamlit secrets")
        st.info("Get your API key from: https://console.groq.com")
        st.stop()
    return Groq(api_key=api_key)

# Initialize Groq client
client = get_groq_client()

# Initialize knowledge bases (this happens automatically on startup)
kb = initialize_knowledge_bases()

# ============================================================================
# INITIALIZE CHAT HISTORY
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# ============================================================================
# DISPLAY CHAT HISTORY
# ============================================================================

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ============================================================================
# CHAT INPUT WITH MULTI-DOMAIN RAG
# ============================================================================

if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response with RAG context
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # === RAG: Retrieve relevant context (auto-detects domain) ===
            relevant_context = kb.get_relevant_context(prompt, k=3)
            
            # Build messages with context
            messages_with_context = []
            
            # Add system prompt
            messages_with_context.append({
                "role": "system",
                "content": SYSTEM_PROMPT
            })
            
            # Add conversation history (excluding system)
            for msg in st.session_state.messages[1:]:  # Skip original system message
                messages_with_context.append(msg)
            
            # If we have relevant context, inject it before the last user message
            if relevant_context:
                # Remove last user message temporarily
                messages_with_context.pop()
                
                # Add context as system message
                messages_with_context.append({
                    "role": "system",
                    "content": f"""
RELEVANT DATABRICKS DOCUMENTATION (use this to provide accurate information):

{relevant_context}

Use the above documentation to answer questions accurately. The documentation is tagged by domain (MIGRATION, OPTIMIZATION, or COSTING). Reference the appropriate domain when answering.
"""
                })
                
                # Re-add user message
                messages_with_context.append({
                    "role": "user",
                    "content": prompt
                })
            
            # Stream response from Groq
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_with_context,
                stream=True,
                max_tokens=2048,
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
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": full_response})

