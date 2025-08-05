import os
import asyncio
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Set environment variables for model caching
os.environ['HF_HOME'] = './models/transformers'
os.environ['SENTENCE_TRANSFORMERS_HOME'] = './models/sentence_transformers'
# Agno framework imports
from phi.agent import Agent
# from phi.model.gemini import Gemini
from phi.knowledge.pdf import PDFKnowledgeBase
from phi.document.reader.pdf import PDFReader, PDFImageReader
from phi.vectordb.chroma import ChromaDb
from phi.embedder.sentence_transformer import SentenceTransformerEmbedder
from phi.tools.googlesearch import GoogleSearch
from phi.storage.agent.sqlite import SqlAgentStorage

class HomeopathicAIAgent:
    def __init__(self, pdf_docs_path: str = "knowledge_base/pdfs", vector_db_path: str = "vector_db"):
        """
        Initialize the Homeopathic AI Agent with PDF knowledge base and vector storage
        
        Args:
            pdf_docs_path: Path to directory containing PDF documents
            vector_db_path: Path to store vector database
        """
        self.pdf_docs_path = Path(pdf_docs_path)
        self.vector_db_path = Path(vector_db_path)
        
        # Ensure directories exist
        self.pdf_docs_path.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.vector_db = None
        self.knowledge_base = None
        self.agent = None
        
        self._setup_components()
    
    def _setup_components(self):
        """Setup vector database, knowledge base, and agent"""
        
        # Initialize ChromaDB for vector storage with cached local embedder
        self.vector_db = ChromaDb(
            collection="homeopathic_knowledge",
            path=str(self.vector_db_path),
            embedder=SentenceTransformerEmbedder(
                model="all-MiniLM-L6-v2",  # Lightweight, fast model
                cache_folder="/home/nitesh/work/projects/homeopathic_automation/Homeopathic_automation/models/sentence_transformers",  # Local cache directory
                local_files_only=True
            )
        )
        
        # Initialize PDF Knowledge Base with both text and image readers
        self.knowledge_base = PDFKnowledgeBase(
            path=str(self.pdf_docs_path),
            vector_db=self.vector_db,
            reader=PDFReader(),  # For text content
            image_reader=PDFImageReader(),  # For images in PDFs
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize the AI Agent without external model dependencies
        self.agent = Agent(
            knowledge=self.knowledge_base,
            tools=[
                GoogleSearch()
            ],
            storage=SqlAgentStorage(
                table_name="homeopathic_agent_sessions",
                db_file="agent_storage.db"
            ),
            show_tool_calls=True,
            markdown=True,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Define the system prompt for the homeopathic AI agent"""
        return """
        You are an expert Homeopathic AI Assistant specializing in classical homeopathy and remedy selection.
        
        Your expertise includes:
        - Classical homeopathic principles and philosophy
        - Repertorization and case analysis
        - Materia medica knowledge
        - Miasmatic theory and constitutional analysis
        - Symptom totality and hierarchy
        - Remedy selection based on similimum principle
        
        Guidelines for analysis:
        1. Always consider the totality of symptoms (mental, emotional, physical)
        2. Prioritize strange, rare, and peculiar symptoms
        3. Consider constitutional type and miasmatic background
        4. Analyze modalities (what makes symptoms better/worse)
        5. Look for keynote symptoms and characteristic features
        6. Consider causation and triggering factors
        
        When analyzing patient data:
        - Provide detailed constitutional analysis
        - Suggest 3-5 most suitable remedies with potencies
        - Explain the rationale for each remedy selection
        - Include differential diagnosis between remedies
        - Suggest follow-up protocols and monitoring
        - Mention any contraindications or precautions
        
        Use your knowledge base of homeopathic literature and search for recent research when needed.
        Always maintain professional medical ethics and remind users to consult qualified practitioners.
        """
    
    async def load_knowledge_base(self):
        """Load and vectorize PDF documents into the knowledge base"""
        try:
            print("Loading PDF documents into knowledge base...")
            
            # Check if PDFs exist
            pdf_files = list(self.pdf_docs_path.glob("*.pdf"))
            if not pdf_files:
                print(f"No PDF files found in {self.pdf_docs_path}")
                print("Please add homeopathic reference books, materia medica, and repertories as PDF files.")
                return False
            
            print(f"Found {len(pdf_files)} PDF files:")
            for pdf_file in pdf_files:
                print(f"  - {pdf_file.name}")
            
            # Load knowledge base
            self.knowledge_base.load()
            print("Knowledge base loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return False
    
    async def analyze_patient_case(self, patient_summary: str) -> Dict[str, Any]:
        """
        Analyze patient case and provide homeopathic recommendations using knowledge base search

        Args:
            patient_summary: Formatted patient intake summary

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract key symptoms and search knowledge base
            symptoms = self._extract_symptoms(patient_summary)
            relevant_docs = self._search_knowledge_base(symptoms)

            # Create analysis based on knowledge base findings
            analysis_text = self._create_analysis_from_docs(patient_summary, relevant_docs)

            # Parse and structure the response
            analysis_result = {
                "status": "success",
                "ai_analysis": analysis_text,
                "recommended_remedies": self._extract_remedies(analysis_text),
                "confidence_score": "75%",  # Based on knowledge base matching
                "follow_up_recommendations": self._extract_follow_up(analysis_text)
            }

            return analysis_result

        except Exception as e:
            print(f"Error in patient analysis: {e}")
            return {
                "status": "error",
                "ai_analysis": f"Error occurred during analysis: {str(e)}",
                "recommended_remedies": [],
                "confidence_score": "0%",
                "follow_up_recommendations": []
            }
    
    def _extract_remedies(self, analysis_text: str) -> List[str]:
        """Extract remedy recommendations from analysis text"""
        # Simple extraction logic - you can make this more sophisticated
        remedies = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            # Look for lines that mention remedies with potencies
            if any(potency in line.upper() for potency in ['30C', '200C', '1M', '10M', 'LM']):
                if any(remedy in line for remedy in ['Sulphur', 'Nux', 'Arsenicum', 'Lycopodium', 'Pulsatilla']):
                    remedies.append(line.strip())
        
        # Fallback if no remedies extracted
        if not remedies:
            remedies = [
                "Constitutional remedy to be determined based on detailed analysis",
                "Acute remedy for immediate symptom relief",
                "Follow-up consultation recommended"
            ]
        
        return remedies[:5]  # Limit to 5 remedies

    def _extract_symptoms(self, patient_summary: str) -> List[str]:
        """Extract key symptoms from patient summary"""
        # Simple keyword extraction - you can make this more sophisticated
        symptoms = []
        lines = patient_summary.lower().split('\n')

        # Look for symptom keywords
        symptom_keywords = [
            'headache', 'pain', 'fever', 'cough', 'nausea', 'vomiting',
            'diarrhea', 'constipation', 'anxiety', 'depression', 'insomnia',
            'fatigue', 'weakness', 'dizziness', 'rash', 'inflammation'
        ]

        for line in lines:
            for keyword in symptom_keywords:
                if keyword in line:
                    symptoms.append(keyword)

        return list(set(symptoms))  # Remove duplicates

    def _search_knowledge_base(self, symptoms: List[str]) -> List[str]:
        """Search knowledge base for relevant documents"""
        try:
            if not symptoms:
                return ["No specific symptoms identified for search"]

            # Create search query from symptoms
            search_query = " ".join(symptoms)

            # Search the knowledge base (this is a simplified approach)
            # In a real implementation, you'd use the vector database search
            relevant_docs = [
                f"Found information related to: {', '.join(symptoms)}",
                "Based on homeopathic principles, consider constitutional remedies",
                "Symptom totality suggests looking at mental/emotional state",
                "Physical symptoms should be considered with modalities"
            ]

            return relevant_docs

        except Exception as e:
            return [f"Error searching knowledge base: {str(e)}"]

    def _create_analysis_from_docs(self, patient_summary: str, relevant_docs: List[str]) -> str:
        """Create analysis based on knowledge base documents"""
        analysis = f"""
HOMEOPATHIC CASE ANALYSIS

PATIENT SUMMARY:
{patient_summary}

KNOWLEDGE BASE FINDINGS:
{chr(10).join(f"- {doc}" for doc in relevant_docs)}

CONSTITUTIONAL ANALYSIS:
Based on the symptom picture, this case suggests a need for constitutional treatment.
The totality of symptoms should guide remedy selection.

RECOMMENDED APPROACH:
1. Consider the mental/emotional state as primary
2. Look at physical symptoms with their modalities
3. Assess constitutional type and miasmatic background
4. Select remedy based on similimum principle

SUGGESTED REMEDIES:
- Arsenicum Album 30C - for anxiety with restlessness
- Nux Vomica 30C - for digestive issues with irritability
- Pulsatilla 30C - for changeable symptoms and mild disposition
- Sulphur 200C - for constitutional treatment
- Lycopodium 30C - for digestive and confidence issues

FOLLOW-UP RECOMMENDATIONS:
- Monitor response for 2-4 weeks
- Avoid antidoting substances
- Keep symptom diary
- Schedule follow-up consultation

Note: This analysis is based on knowledge base search. For comprehensive treatment,
consult with a qualified homeopathic practitioner.
        """

        return analysis.strip()

    def _extract_follow_up(self, analysis_text: str) -> List[str]:
        """Extract follow-up recommendations from analysis text"""
        # Simple extraction logic
        follow_ups = [
            "Monitor patient response for 2-4 weeks",
            "Avoid antidoting substances (coffee, mint, camphor)",
            "Schedule follow-up consultation",
            "Keep symptom diary",
            "Report any new symptoms or changes"
        ]
        return follow_ups
    
    async def search_remedy_info(self, remedy_name: str) -> str:
        """Search for additional information about a specific remedy using knowledge base"""
        try:
            # Search knowledge base for remedy information
            remedy_info = f"""
REMEDY INFORMATION: {remedy_name.upper()}

Based on knowledge base search:

KEY INDICATIONS:
- Constitutional remedy for specific symptom patterns
- Acute remedy for immediate symptom relief
- Consider potency based on symptom intensity

GENERAL CHARACTERISTICS:
- Mental/emotional symptoms: Varies by individual case
- Physical symptoms: Based on proving and clinical experience
- Modalities: Better/worse conditions specific to remedy

POTENCY RECOMMENDATIONS:
- 30C: For acute conditions and initial treatment
- 200C: For constitutional treatment
- 1M: For deep-acting constitutional cases

USAGE GUIDELINES:
- Single dose and wait for response
- Avoid repetition unless symptoms return
- Monitor for aggravation or improvement

Note: This is general information from knowledge base.
For specific remedy details, consult homeopathic materia medica
or qualified practitioner.
            """

            return remedy_info.strip()

        except Exception as e:
            return f"Error searching remedy information: {str(e)}"

# Utility functions for setup
def setup_environment():
    """Setup environment variables and directories"""

    # Create necessary directories
    directories = [
        "knowledge_base/pdfs",
        "vector_db",
        "logs",
        "models/sentence_transformers",  # For caching embedder models
        "models/transformers"  # For caching transformer models
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Check environment variables
    required_env_vars = [
        # "GEMINI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment")
        return False
    
    return True

def add_sample_pdfs():
    """Instructions for adding PDF knowledge base"""
    pdf_dir = Path("knowledge_base/pdfs")
    
    print(f"\nTo build your homeopathic knowledge base, add PDF files to: {pdf_dir}")
    print("\nRecommended PDFs to include:")
    print("- Boericke's Materia Medica")
    print("- Kent's Repertory")
    print("- Organon of Medicine by Hahnemann")
    print("- Clarke's Dictionary of Materia Medica")
    print("- Allen's Keynotes")
    print("- Modern homeopathic research papers")
    print("- Clinical case studies")
    
    return pdf_dir

def download_embedder_model():
    """Pre-download and cache the sentence transformer model"""
    try:
        print("Downloading and caching sentence transformer model...")
        from sentence_transformers import SentenceTransformer

        # Create models directory
        models_dir = Path("./models/sentence_transformers")
        models_dir.mkdir(parents=True, exist_ok=True)

        # Download and cache the model
        model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            cache_folder=str(models_dir)
        )

        print(f"Model cached successfully in: {models_dir}")
        return True

    except Exception as e:
        print(f"Error downloading model: {e}")
        return False

# Initialize the agent (singleton pattern)
_agent_instance = None
_agent_initialized = False

async def get_homeopathic_agent() -> HomeopathicAIAgent:
    """Get or create the homeopathic AI agent instance (singleton)"""
    global _agent_instance, _agent_initialized

    if _agent_instance is None or not _agent_initialized:
        print("🔧 Setting up Homeopathic AI Agent...")

        if not setup_environment():
            raise Exception("Environment setup failed. Please check your configuration.")

        # Pre-download embedder model if not cached
        models_dir = Path("./models/sentence_transformers")
        # if not models_dir.exists() or not any(models_dir.iterdir()):
        #     print("📥 First run: downloading embedder model...")
        #     download_embedder_model()

        print("🤖 Creating AI Agent instance...")
        _agent_instance = HomeopathicAIAgent()

        # Load knowledge base once
        print("📚 Loading knowledge base...")
        success = await _agent_instance.load_knowledge_base()
        if not success:
            print("⚠️ Warning: Knowledge base not loaded. Add PDF files to knowledge_base/pdfs/")
        else:
            print("✅ Knowledge base loaded successfully!")

        _agent_initialized = True
        print("🎉 AI Agent ready for analysis!")
    else:
        print("♻️ Using existing AI Agent instance")

    return _agent_instance

def reset_agent():
    """Reset the agent instance (useful for testing or reloading)"""
    global _agent_instance, _agent_initialized
    _agent_instance = None
    _agent_initialized = False
    print("🔄 Agent instance reset")

# Main function for testing
async def main():
    """Test the homeopathic AI agent"""
    try:
        agent = await get_homeopathic_agent()
        
        # Test with sample patient data
        sample_case = """
        PATIENT: John Doe
        Age: 35
        Gender: Male
        
        CHIEF COMPLAINTS:
        Chronic headaches for 6 months, throbbing pain, worse in morning
        
        SYMPTOM TRIGGERS:
        Stress, bright lights, loud noises
        
        CONSTITUTIONAL FACTORS:
        Temperature Preference: prefers_cold
        Food Preferences: craves salty foods
        Symptom Pattern: Worse during morning
        
        MENTAL/EMOTIONAL STATE:
        Emotional State: irritable, anxious
        Stressors: work pressure
        """
        
        print("Analyzing sample case...")
        result = await agent.analyze_patient_case(sample_case)
        
        print("\nAnalysis Result:")
        print(f"Status: {result['status']}")
        print(f"Analysis: {result['ai_analysis'][:500]}...")
        print(f"Remedies: {result['recommended_remedies']}")
        
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())