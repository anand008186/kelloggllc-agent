#!/usr/bin/env python3
"""
Intelligent QA Agent that uses Agno for decision-making with structured workflow.
"""

import os
import time
import signal
import sys
from textwrap import dedent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv('OPENAI_API_KEY'):
    print("❌ ERROR: OPENAI_API_KEY not found!")
    exit(1)

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import Function

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global shutdown_flag
    print("\n🛑 Shutdown signal received. Stopping watcher...")
    shutdown_flag = True

# Set up signal handler
signal.signal(signal.SIGINT, signal_handler)

# Import the functions from asana_form_agent
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

def process_single_task(task_id, task_name):
    """Process a single task with intelligent decision making."""
    print(f"\n🧠 Processing Task: {task_name}")
    print(f"🆔 Task ID: {task_id}")
    print("-" * 40)
    
    # Step 1: Move to processing
    print("🔄 Moving task to Processing...")
    move_task_to_processing(task_id)
    
    # Step 2: Try to download PDF
    print("📥 Attempting to download PDF...")
    pdf_path = download_pdf_from_task(task_id)
    
    if pdf_path:
        print(f"✅ PDF downloaded successfully: {pdf_path}")
        
        # Step 3: Extract form information
        print("🔍 Extracting form information...")
        form_info = extract_form_info(pdf_path)
        
        if form_info and form_info.get('form_type') == '471':
            print(f"✅ Form 471 detected with establishing Form 470 number: {form_info.get('establishing_form470_number')}")
            
            # Step 4: Search for Form 470
            print("🔍 Searching for corresponding Form 470...")
            search_result = search_form470(form_info)
            
            if search_result.get('found'):
                print("🎉 Form 470 found! Marking task as complete.")
                mark_task_complete(task_id, search_result.get('form470_url'))
                return "COMPLETED"
            else:
                print("📝 Form 470 not found. Moving to manual follow-up.")
                move_task_to_manual_followup(task_id, "Form 470 not found in USAC database")
                create_manual_review_subtask(task_id, form_info)
                return "MANUAL_FOLLOWUP"
        else:
            print("⚠️ Not a Form 471 or form info extraction failed. Moving to issues.")
            move_task_to_issues(task_id, "Not a Form 471 or extraction failed")
            return "ISSUES"
    else:
        print("❌ No PDF found or download failed. Moving to issues.")
        move_task_to_issues(task_id, "No PDF found or download failed")
        return "ISSUES"

def get_qa_tasks_for_agent():
    """Get QA tasks for the agent to process."""
    print("📋 Getting QA tasks...")
    qa_tasks = get_qa_tasks()
    print(f"✅ Found {len(qa_tasks)} QA tasks")
    return qa_tasks

def analyze_task_decision(task_id, task_name, pdf_status, form_info=None, search_result=None):
    """Let the AI agent make intelligent decisions about task processing."""
    
    # Create the intelligent agent
    intelligent_agent = Agent(
        model=OpenAIChat(id="gpt-4.1-nano"),
        tools=[
            Function(
                name="move_task_to_processing",
                description="Move task to QA – Processing section",
                func=move_task_to_processing
            ),
            Function(
                name="mark_task_complete",
                description="Mark task as complete with Form 470 URL",
                func=mark_task_complete
            ),
            Function(
                name="move_task_to_manual_followup",
                description="Move task to QA – Manual Follow-up Required section",
                func=move_task_to_manual_followup
            ),
            Function(
                name="create_manual_review_subtask",
                description="Create a sub-task for manual review when Form 470 is not found",
                func=create_manual_review_subtask
            ),
            Function(
                name="move_task_to_issues",
                description="Move task to QA - Issues section",
                func=move_task_to_issues
            )
        ],
        instructions=dedent("""\
            You are an intelligent QA workflow agent. Analyze the task processing results and make the appropriate decision.
            
            TASK ANALYSIS:
            - Task ID: {task_id}
            - Task Name: {task_name}
            - PDF Status: {pdf_status}
            - Form Info: {form_info}
            - Search Result: {search_result}
            
            DECISION RULES:
            1. If PDF download failed: Move task to Issues
            2. If Form 471 found but no Form 470: Move to Manual Follow-up + create sub-task
            3. If Form 471 found and Form 470 found: Mark task as complete
            4. If not Form 471: Move to Issues
            
            Make the appropriate decision and call the necessary tools.
            """),
        add_datetime_to_instructions=True,
        show_tool_calls=True,
        markdown=True,
    )
    
    # Let the agent make the decision
    intelligent_agent.print_response(
        f"Analyze task {task_id} ({task_name}) with PDF status: {pdf_status}, form info: {form_info}, search result: {search_result}. Make the appropriate decision.",
        stream=True
    )

def process_qa_tasks_intelligently():
    """Process QA tasks with intelligent decision making."""
    
    print("🧠 Starting Intelligent QA Task Processing...")
    print("=" * 60)
    
    # Get QA tasks
    qa_tasks = get_qa_tasks_for_agent()
    
    if not qa_tasks:
        print("❌ No QA tasks found!")
        return
    
    # Process each task
    for i, task in enumerate(qa_tasks, 1):
        task_id = task.get('gid')
        task_name = task.get('name')
        
        print(f"\n🔄 Processing Task {i}/{len(qa_tasks)}")
        print("=" * 50)
        
        # Process the task and get the result
        result = process_single_task(task_id, task_name)
        
        print(f"✅ Task processing result: {result}")
        print("=" * 50)
    
    print("\n🎉 All QA tasks processed intelligently!")

def run_watcher_mode():
    """Run the intelligent agent in continuous monitoring mode."""
    print("🧠 INTELLIGENT QA AGENT - WATCHER MODE")
    print("=" * 60)
    print("✅ Environment variables configured")
    print("⏱️  Check interval: 60 seconds")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    run_count = 0
    
    while not shutdown_flag:
        run_count += 1
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n🔄 Run #{run_count} - {current_time}")
        print("🧠 Processing QA tasks intelligently...")
        print("=" * 60)
        
        try:
            process_qa_tasks_intelligently()
            print(f"✅ Run #{run_count} completed successfully")
            
        except Exception as e:
            print(f"❌ Error in run #{run_count}: {str(e)}")
        
        if not shutdown_flag:
            print("⏳ Waiting 60 seconds until next run...")
            time.sleep(60)
    
    print("🛑 Intelligent watcher mode stopped.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watcher":
        # Run in watcher mode
        run_watcher_mode()
    else:
        # Run once
        process_qa_tasks_intelligently() 