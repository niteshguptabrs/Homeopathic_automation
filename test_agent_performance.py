#!/usr/bin/env python3
"""
Test script to verify that the AI agent is initialized only once
and subsequent calls are much faster.
"""

import asyncio
import time
from ai_agent import get_homeopathic_agent, reset_agent

async def test_agent_initialization_performance():
    """Test that agent initialization happens only once"""
    
    print("=== AI Agent Performance Test ===\n")
    
    # Reset agent to ensure clean test
    reset_agent()
    
    # Test 1: First call (should initialize)
    print("🧪 Test 1: First agent call (should initialize)")
    start_time = time.time()
    agent1 = await get_homeopathic_agent()
    first_call_time = time.time() - start_time
    print(f"⏱️ First call took: {first_call_time:.2f} seconds\n")
    
    # Test 2: Second call (should reuse existing)
    print("🧪 Test 2: Second agent call (should reuse existing)")
    start_time = time.time()
    agent2 = await get_homeopathic_agent()
    second_call_time = time.time() - start_time
    print(f"⏱️ Second call took: {second_call_time:.2f} seconds\n")
    
    # Test 3: Third call (should reuse existing)
    print("🧪 Test 3: Third agent call (should reuse existing)")
    start_time = time.time()
    agent3 = await get_homeopathic_agent()
    third_call_time = time.time() - start_time
    print(f"⏱️ Third call took: {third_call_time:.2f} seconds\n")
    
    # Verify same instance
    print("🔍 Instance verification:")
    print(f"Agent 1 ID: {id(agent1)}")
    print(f"Agent 2 ID: {id(agent2)}")
    print(f"Agent 3 ID: {id(agent3)}")
    print(f"Same instance: {agent1 is agent2 is agent3}\n")
    
    # Performance summary
    print("📊 Performance Summary:")
    print(f"First call (initialization): {first_call_time:.2f}s")
    print(f"Second call (reuse): {second_call_time:.2f}s")
    print(f"Third call (reuse): {third_call_time:.2f}s")
    
    if second_call_time < first_call_time * 0.1:  # Should be at least 10x faster
        print("✅ Performance optimization working correctly!")
    else:
        print("⚠️ Performance optimization may not be working as expected")
    
    return agent1

async def test_analysis_performance():
    """Test analysis performance with reused agent"""
    
    print("\n=== Analysis Performance Test ===\n")
    
    agent = await get_homeopathic_agent()
    
    sample_case = """
    PATIENT: Test Patient
    Age: 30
    Gender: Female
    
    CHIEF COMPLAINTS:
    Chronic headaches, fatigue, digestive issues
    
    MENTAL/EMOTIONAL STATE:
    Anxious, irritable, stressed from work
    
    CONSTITUTIONAL FACTORS:
    Prefers warm weather, craves salty foods
    """
    
    # Test multiple analyses
    analysis_times = []
    
    for i in range(3):
        print(f"🧪 Analysis {i+1}:")
        start_time = time.time()
        result = await agent.analyze_patient_case(sample_case)
        analysis_time = time.time() - start_time
        analysis_times.append(analysis_time)
        
        print(f"⏱️ Analysis took: {analysis_time:.2f} seconds")
        print(f"📋 Status: {result['status']}")
        print(f"💊 Remedies found: {len(result['recommended_remedies'])}")
        print()
    
    avg_time = sum(analysis_times) / len(analysis_times)
    print(f"📊 Average analysis time: {avg_time:.2f} seconds")
    
    if all(t < 2.0 for t in analysis_times):  # Should be under 2 seconds
        print("✅ Analysis performance is good!")
    else:
        print("⚠️ Analysis might be slower than expected")

async def main():
    """Run all performance tests"""
    try:
        # Test agent initialization
        agent = await test_agent_initialization_performance()
        
        # Test analysis performance
        await test_analysis_performance()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
