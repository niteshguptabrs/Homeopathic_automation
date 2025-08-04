import json
from fastapi import FastAPI, Form
from pydantic import BaseModel
from typing import Optional, Annotated
import uvicorn

app = FastAPI(title="Homeopathic Patient Intake API")

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

@app.post("/submit-intake")
async def submit_intake(data: Annotated[PatientIntakeForm, Form()]):
    # Generate patient summary
    summary = generate_patient_summary(data)
    summarized_data={
        "status": "success",
        "message": "Patient intake form submitted successfully",
        "patient_data": data.dict(),
        "patient_summary": summary
    }
    # json.dump(summarized_data, open("patient_data.json", "w"))
    return summarized_data

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