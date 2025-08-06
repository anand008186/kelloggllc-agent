#!/usr/bin/env python3
"""
Test script to manually test the QA task processing workflow.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_qa_processing():
    """Test the complete QA processing workflow manually."""
    
    print("🧪 Testing QA Task Processing Workflow")
    print("=" * 50)
    
    try:
        # Import the functions
        from asana_form_agent import get_qa_tasks, download_pdf_from_task, extract_form_info, search_form470
        
        # Step 1: Get QA tasks
        print("\n📋 Step 1: Getting QA tasks...")
        qa_tasks = get_qa_tasks()
        print(f"✅ Found {len(qa_tasks)} QA tasks")
        
        if not qa_tasks:
            print("❌ No QA tasks found!")
            return
        
        # Step 2: Process each task
        for i, task in enumerate(qa_tasks, 1):
            task_id = task.get('gid')
            task_name = task.get('name')
            
            print(f"\n🔄 Processing Task {i}/{len(qa_tasks)}: {task_name}")
            print(f"🆔 Task ID: {task_id}")
            print("-" * 40)
            
            # Step 2a: Download PDF
            print("📥 Step 2a: Downloading PDF...")
            pdf_path = download_pdf_from_task(task_id)
            
            if pdf_path:
                print(f"✅ PDF downloaded: {pdf_path}")
                
                # Step 2b: Extract form info
                print("🔍 Step 2b: Extracting form info...")
                form_info = extract_form_info(pdf_path)
                
                if form_info:
                    print(f"✅ Form info extracted: {form_info}")
                    
                    # Step 2c: Search for Form 470
                    print("🔍 Step 2c: Searching for Form 470...")
                    search_result = search_form470(form_info)
                    
                    if search_result.get('found'):
                        print(f"✅ Form 470 found: {search_result.get('form470_url')}")
                        print("🎉 Task should be marked as complete!")
                    else:
                        print(f"❌ Form 470 not found: {search_result.get('error', 'Unknown error')}")
                        print("📝 Task should be moved to Manual Follow-up Required")
                else:
                    print("❌ No form info extracted")
                    print("⚠️ Task should be moved to Issues")
            else:
                print("❌ No PDF found or download failed")
                print("⚠️ Task should be moved to Issues")
            
            print("=" * 50)
        
        print("\n✅ QA processing test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    test_qa_processing() 