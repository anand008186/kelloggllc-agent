#!/usr/bin/env python3
"""
Dedicated runner for QA task processing that directly calls the functions.
"""

import os
import time
import signal
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv('OPENAI_API_KEY'):
    print("❌ ERROR: OPENAI_API_KEY not found!")
    exit(1)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global shutdown_flag
    print("\n🛑 Shutdown signal received. Stopping watcher...")
    shutdown_flag = True

# Set up signal handler
signal.signal(signal.SIGINT, signal_handler)

def process_qa_tasks():
    """Process all QA tasks using the direct function calls."""
    
    print("🚀 Starting QA task processing...")
    print("=" * 50)
    
    try:
        # Import the functions
        from asana_form_agent import (
            get_qa_tasks, 
            move_task_to_processing, 
            download_pdf_from_task, 
            extract_form_info, 
            search_form470, 
            mark_task_complete, 
            move_task_to_manual_followup, 
            create_manual_review_subtask, 
            move_task_to_issues
        )
        
        # Step 1: Get QA tasks
        print("📋 Step 1: Getting QA tasks...")
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
            
            # Step 2a: Move task to processing
            print("🔄 Step 2a: Moving task to Processing section...")
            move_task_to_processing(task_id)
            
            # Step 2b: Download PDF
            print("📥 Step 2b: Downloading PDF...")
            pdf_path = download_pdf_from_task(task_id)
            
            if pdf_path:
                print(f"✅ PDF downloaded: {pdf_path}")
                
                # Step 2c: Extract form info
                print("🔍 Step 2c: Extracting form info...")
                form_info = extract_form_info(pdf_path)
                
                if form_info:
                    print(f"✅ Form info extracted: {form_info}")
                    
                    # Step 2d: Search for Form 470
                    print("🔍 Step 2d: Searching for Form 470...")
                    search_result = search_form470(form_info)
                    
                    if search_result.get('found'):
                        print(f"✅ Form 470 found: {search_result.get('form470_url')}")
                        print("🎉 Marking task as complete!")
                        mark_task_complete(task_id, search_result.get('form470_url'))
                    else:
                        print(f"❌ Form 470 not found: {search_result.get('error', 'Unknown error')}")
                        print("📝 Moving task to Manual Follow-up Required and creating sub-task...")
                        move_task_to_manual_followup(task_id, "Form 470 not found in USAC database")
                        create_manual_review_subtask(task_id, form_info)
                else:
                    print("❌ No form info extracted")
                    print("⚠️ Moving task to Issues...")
                    move_task_to_issues(task_id, "Failed to extract form information from PDF")
            else:
                print("❌ No PDF found or download failed")
                print("⚠️ Moving task to Issues...")
                move_task_to_issues(task_id, "No PDF found or download failed")
            
            print("=" * 50)
        
        print("\n✅ All QA tasks processed!")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")

def run_watcher_mode():
    """Run the agent in continuous monitoring mode."""
    print("🚀 QA AGENT - WATCHER MODE")
    print("=" * 50)
    print("✅ Environment variables configured")
    print("⏱️  Check interval: 60 seconds")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    run_count = 0
    
    while not shutdown_flag:
        run_count += 1
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n🔄 Run #{run_count} - {current_time}")
        print("🚀 Processing QA tasks...")
        print("=" * 50)
        
        try:
            process_qa_tasks()
            print(f"✅ Run #{run_count} completed successfully")
            
        except Exception as e:
            print(f"❌ Error in run #{run_count}: {str(e)}")
        
        if not shutdown_flag:
            print("⏳ Waiting 60 seconds until next run...")
            time.sleep(60)
    
    print("🛑 Watcher mode stopped.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watcher":
        # Run in watcher mode
        run_watcher_mode()
    else:
        # Run once
        process_qa_tasks() 