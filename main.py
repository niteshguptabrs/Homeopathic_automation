import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Annotated
import uvicorn
import os

app = FastAPI(title="Homeopathic Patient Intake API")

# Mount static files directory to serve images, CSS, JS files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize the AI agent once when the app starts"""
    global global_agent
    print("🚀 Initializing Homeopathic AI Agent...")
    try:
        global_agent = await get_homeopathic_agent()
        print("✅ AI Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize AI Agent: {e}")
        global_agent = None
# Import and use the AI agent
from ai_agent import get_homeopathic_agent

# Global agent instance - initialized once
global_agent = None

# Store the latest patient data (in production, use a database)
latest_patient_data = {}

class PatientIntakeForm(BaseModel):
    # Patient Information
    fullName: str
    age: Optional[str] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None
    
    # Chief Complaints
    mainSymptoms: Optional[str] = None
    symptomTriggers: Optional[str] = None
    symptomRelief: Optional[str] = None
    
    # Medical History
    pastIllnesses: Optional[str] = None
    currentMedications: Optional[str] = None
    familyHistory: Optional[str] = None
    allergies: Optional[str] = None
    
    # Lifestyle and Environment
    diet: Optional[str] = None
    sleep: Optional[str] = None
    exercise: Optional[str] = None
    environment: Optional[str] = None
    
    # Emotional and Mental State
    emotionalState: Optional[str] = None
    stressors: Optional[str] = None
    mentalSymptoms: Optional[str] = None
    
    # General Preferences and Sensitivities
    temperature: Optional[str] = None
    foodPreferences: Optional[str] = None
    timeOfDay: Optional[str] = None
    
    # Doctor's Observations
    doctorObservations: Optional[str] = None
    suspectedOrgan: Optional[str] = None
    relatedBodyParts: Optional[str] = None
    diagnosisNotes: Optional[str] = None
    prescribedRemedy: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def serve_form():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/submit-intake")
async def submit_intake(data: Annotated[PatientIntakeForm, Form()]):
    global latest_patient_data
    
    # Generate patient summary
    summary = generate_patient_summary(data)
    
    # Store data globally (use database in production)
    latest_patient_data = {
        "status": "success",
        "message": "Patient intake form submitted successfully",
        "patient_data": data.dict(),
        "patient_summary": summary
    }
    
    # Save to JSON file for persistence
    with open("patient_data.json", "w") as f:
        json.dump(latest_patient_data, f, indent=2)
    
    return RedirectResponse(url="http://0.0.0.0:8000/success", status_code=303)

@app.get("/success", response_class=HTMLResponse)
async def success_page():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Form Submitted Successfully</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-b from-green-50 to-green-100 min-h-screen flex items-center justify-center">
        <div class="bg-white p-8 rounded-xl shadow-lg text-center max-w-md">
            <div class="text-green-600 text-6xl mb-4">✓</div>
            <h1 class="text-2xl font-bold text-gray-800 mb-4">Form Submitted Successfully!</h1>
            <p class="text-gray-600 mb-6">Patient intake form has been processed successfully.</p>
            <button onclick="viewSummary()" class="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors">
                View Patient Summary
            </button>
        </div>
        
        <script>
            function viewSummary() {
                window.location.href = '/patient-summary';
            }
        </script>
    </body>
    </html>
    """)

@app.get("/patient-summary", response_class=HTMLResponse)
async def patient_summary_page():
    global latest_patient_data
    
    if not latest_patient_data:
        return HTMLResponse(content="""
        <html><body><h1>No patient data found</h1><a href="/">Go back to form</a></body></html>
        """)
    
    summary = latest_patient_data.get("patient_summary", "No summary available")
    patient_name = latest_patient_data.get("patient_data", {}).get("fullName", "Unknown Patient")
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Patient Summary - {patient_name}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .summary-content {{
                white-space: pre-wrap;
                line-height: 1.6;
            }}
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            .animate-spin {{
                animation: spin 1s linear infinite;
            }}
            @media print {{
                .no-print {{
                    display: none !important;
                }}
            }}
        </style>
    </head>
    <body class="bg-gradient-to-b from-blue-50 to-blue-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                <div class="bg-blue-600 text-white p-6">
                    <h1 class="text-3xl font-bold">Patient Summary</h1>
                    <p class="text-blue-100 mt-2">Comprehensive intake analysis</p>
                </div>
                
                <div class="p-8">
                    <div class="bg-gray-50 p-6 rounded-lg mb-6">
                        <div class="summary-content text-gray-800 font-mono text-sm">{summary}</div>
                    </div>
                    
                    <div class="flex gap-4 justify-center">
                        <button onclick="sendToAI()" class="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors">
                            Send to AI for Analysis
                        </button>
                        <button onclick="downloadSummary()" class="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors">
                            Download Summary
                        </button>
                        <a href="/" class="bg-gray-600 text-white px-6 py-3 rounded-md hover:bg-gray-700 transition-colors inline-block">
                            New Patient
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function sendToAI() {{
                // Show loading state
                const aiButton = document.querySelector('button[onclick="sendToAI()"]');
                const originalText = aiButton.textContent;
                aiButton.innerHTML = '<span class="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>Analyzing...';
                aiButton.disabled = true;
                
                // Hide existing AI analysis if any
                const existingAnalysis = document.getElementById('ai-analysis-section');
                if (existingAnalysis) {{
                    existingAnalysis.remove();
                }}
                
                // Make API call to AI service
                fetch('/analyze-with-ai', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{summary: `{summary}`}})
                }})
                .then(response => response.json())
                .then(data => {{
                    console.log('AI Analysis:', data);
                    
                    // Reset button
                    aiButton.textContent = originalText;
                    aiButton.disabled = false;
                    
                    // Display AI analysis results
                    displayAIAnalysis(data);
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    
                    // Reset button
                    aiButton.textContent = originalText;
                    aiButton.disabled = false;
                    
                    alert('Error analyzing with AI. Please try again.');
                }});
            }}
            
            function displayAIAnalysis(analysisData) {{
                const summaryContainer = document.querySelector('.p-8');
                
                // Create AI analysis section
                const aiSection = document.createElement('div');
                aiSection.id = 'ai-analysis-section';
                aiSection.className = 'mt-8 bg-gradient-to-r from-purple-50 to-indigo-50 p-6 rounded-lg border-l-4 border-purple-500';
                
                aiSection.innerHTML = `
                    <div class="flex items-center mb-4">
                        <div class="bg-purple-600 text-white p-2 rounded-full mr-3">
                            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <h2 class="text-2xl font-bold text-purple-800">AI Analysis Report</h2>
                    </div>
                    
                    <div class="space-y-4">
                        <div class="bg-white p-4 rounded-lg shadow-sm">
                            <h3 class="font-semibold text-gray-800 mb-2">Analysis Status:</h3>
                            <p class="text-green-600 font-medium">${{analysisData.status || 'Completed'}}</p>
                        </div>
                        
                        <div class="bg-white p-4 rounded-lg shadow-sm">
                            <h3 class="font-semibold text-gray-800 mb-2">AI Analysis:</h3>
                            <p class="text-gray-700 whitespace-pre-wrap">${{analysisData.ai_analysis || 'No analysis available'}}</p>
                        </div>
                        
                        <div class="bg-white p-4 rounded-lg shadow-sm">
                            <h3 class="font-semibold text-gray-800 mb-2">Recommended Remedies:</h3>
                            <ul class="list-disc list-inside text-gray-700 space-y-1">
                                ${{(analysisData.recommended_remedies || []).map(remedy => `<li>${{remedy}}</li>`).join('')}}
                            </ul>
                        </div>
                        
                        <div class="flex gap-3 mt-4">
                            <button onclick="downloadAIReport()" class="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors text-sm">
                                Download AI Report
                            </button>
                            <button onclick="printReport()" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors text-sm">
                                Print Report
                            </button>
                        </div>
                    </div>
                `;
                
                // Insert before the button container
                const buttonContainer = summaryContainer.querySelector('.flex.gap-4.justify-center');
                summaryContainer.insertBefore(aiSection, buttonContainer);
                
                // Smooth scroll to AI analysis
                aiSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
            
            function downloadAIReport() {{
                const aiAnalysis = document.getElementById('ai-analysis-section');
                if (aiAnalysis) {{
                    const reportText = aiAnalysis.innerText;
                    const element = document.createElement('a');
                    const file = new Blob([reportText], {{type: 'text/plain'}});
                    element.href = URL.createObjectURL(file);
                    element.download = '{patient_name}_AI_Analysis.txt';
                    document.body.appendChild(element);
                    element.click();
                    document.body.removeChild(element);
                }}
            }}
            
            function printReport() {{
                window.print();
            }}
            
            function downloadSummary() {{
                const element = document.createElement('a');
                const file = new Blob([`{summary}`], {{type: 'text/plain'}});
                element.href = URL.createObjectURL(file);
                element.download = '{patient_name}_summary.txt';
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
            }}
        </script>
    </body>
    </html>
    """)

# AI integration endpoint
@app.post("/analyze-with-ai")
async def analyze_with_ai(request: Request):
    global global_agent
    data = await request.json()
    summary = data.get("summary", "")

    try:
        # Check if agent is initialized
        if global_agent is None:
            print("⚠️ Agent not initialized, attempting to initialize now...")
            global_agent = await get_homeopathic_agent()

        # Analyze the patient case using the global agent
        result = await global_agent.analyze_patient_case(summary)

        return result
        
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        # Fallback to mock response if AI fails
        return {
            "status": "Analysis Complete (Fallback Mode)",
            "ai_analysis": f"""AI Analysis temporarily unavailable. Error: {str(e)}

FALLBACK ANALYSIS:
Based on the provided patient information, a comprehensive homeopathic analysis would consider:

1. Constitutional assessment based on physical and mental symptoms
2. Miasmatic evaluation considering chronic patterns
3. Symptom totality including modalities and peculiarities
4. Remedy selection based on similimum principle

Please consult with a qualified homeopathic practitioner for proper case analysis.""",
            "recommended_remedies": [
                "Constitutional remedy - to be determined by qualified practitioner",
                "Symptomatic remedy - based on acute presentation",
                "Follow-up consultation recommended"
            ],
            "confidence_score": "N/A",
            "follow_up_recommendations": [
                "Consult qualified homeopathic practitioner",
                "Provide complete case history",
                "Monitor symptom changes"
            ]
        }

@app.get("/agent-status")
async def agent_status():
    """Check the status of the AI agent"""
    global global_agent
    return {
        "agent_initialized": global_agent is not None,
        "status": "ready" if global_agent is not None else "not_initialized",
        "message": "AI Agent is ready for analysis" if global_agent is not None else "AI Agent is not initialized"
    }

def generate_patient_summary(data: PatientIntakeForm) -> str:
    summary_parts = []
    
    # Patient Demographics
    summary_parts.append(f"PATIENT: {data.fullName}")
    if data.age:
        summary_parts.append(f"Age: {data.age}")
    if data.gender:
        summary_parts.append(f"Gender: {data.gender}")
    
    # Chief Complaints
    if data.mainSymptoms:
        summary_parts.append(f"\nCHIEF COMPLAINTS:\n{data.mainSymptoms}")
    
    if data.symptomTriggers:
        summary_parts.append(f"\nSYMPTOM TRIGGERS:\n{data.symptomTriggers}")
    
    if data.symptomRelief:
        summary_parts.append(f"\nSYMPTOM RELIEF FACTORS:\n{data.symptomRelief}")
    
    # Medical History
    medical_history = []
    if data.pastIllnesses:
        medical_history.append(f"Past Illnesses: {data.pastIllnesses}")
    if data.currentMedications:
        medical_history.append(f"Current Medications: {data.currentMedications}")
    if data.familyHistory:
        medical_history.append(f"Family History: {data.familyHistory}")
    if data.allergies:
        medical_history.append(f"Allergies: {data.allergies}")
    
    if medical_history:
        summary_parts.append(f"\nMEDICAL HISTORY:\n" + "\n".join(medical_history))
    
    # Lifestyle Factors
    lifestyle = []
    if data.diet:
        lifestyle.append(f"Diet: {data.diet}")
    if data.sleep:
        lifestyle.append(f"Sleep: {data.sleep}")
    if data.exercise:
        lifestyle.append(f"Exercise: {data.exercise}")
    if data.environment:
        lifestyle.append(f"Environment: {data.environment}")
    
    if lifestyle:
        summary_parts.append(f"\nLIFESTYLE FACTORS:\n" + "\n".join(lifestyle))
    
    # Mental/Emotional State
    mental_state = []
    if data.emotionalState:
        mental_state.append(f"Emotional State: {data.emotionalState}")
    if data.stressors:
        mental_state.append(f"Stressors: {data.stressors}")
    if data.mentalSymptoms:
        mental_state.append(f"Mental Symptoms: {data.mentalSymptoms}")
    
    if mental_state:
        summary_parts.append(f"\nMENTAL/EMOTIONAL STATE:\n" + "\n".join(mental_state))
    
    # Constitutional Factors
    constitutional = []
    if data.temperature:
        constitutional.append(f"Temperature Preference: {data.temperature}")
    if data.foodPreferences:
        constitutional.append(f"Food Preferences: {data.foodPreferences}")
    if data.timeOfDay:
        constitutional.append(f"Symptom Pattern: Worse during {data.timeOfDay}")
    
    if constitutional:
        summary_parts.append(f"\nCONSTITUTIONAL FACTORS:\n" + "\n".join(constitutional))
    
    # Doctor's Assessment
    if data.doctorObservations or data.suspectedOrgan or data.diagnosisNotes:
        assessment = []
        if data.doctorObservations:
            assessment.append(f"Observations: {data.doctorObservations}")
        if data.suspectedOrgan:
            assessment.append(f"Suspected System: {data.suspectedOrgan}")
        if data.relatedBodyParts:
            assessment.append(f"Affected Areas: {data.relatedBodyParts}")
        if data.diagnosisNotes:
            assessment.append(f"Diagnosis Notes: {data.diagnosisNotes}")
        if data.prescribedRemedy:
            assessment.append(f"Prescribed Remedy: {data.prescribedRemedy}")
        
        summary_parts.append(f"\nDOCTOR'S ASSESSMENT:\n" + "\n".join(assessment))
    
    return "\n".join(summary_parts)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
