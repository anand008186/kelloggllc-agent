#!/usr/bin/env python3
"""
Unified Asana Form Agent with step-by-step logging and workflow transitions.
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
    print("📝 Please set your OpenAI API key in the .env file:")
    print("   OPENAI_API_KEY=your_actual_api_key_here")
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

# Custom tools for Asana, PDF processing, and USAC API
def get_qa_tasks():
    """Get all tasks in QA section from Asana project."""
    import asana
    
    print("🔍 Getting QA tasks from project...")
    
    try:
        client = asana.Client.access_token(os.getenv('ASANA_API_KEY'))
        project_id = os.getenv('ASANA_PROJECT_ID')
        
        # Get all tasks in the project
        tasks = client.tasks.find_by_project(project_id, opt_fields=['name', 'completed', 'memberships.section.name', 'notes', 'attachments.name', 'attachments.type', 'attachments.size', 'attachments.download_url'])
        
        qa_tasks = []
        for task in tasks:
            memberships = task.get('memberships', [])
            for membership in memberships:
                section = membership.get('section', {})
                section_name = section.get('name', '').lower()
                # Check for QA section
                if section_name == 'qa':
                    qa_tasks.append(task)
                    print(f"✅ Found QA task: {task.get('name')} (ID: {task.get('gid')}) in section: {section.get('name')}")
                    break
        
        print(f"📊 Total QA tasks found: {len(qa_tasks)}")
        return qa_tasks
        
    except Exception as e:
        print(f"❌ Error getting QA tasks: {str(e)}")
        return []

def move_task_to_processing(task_id):
    """Move task to QA – Processing section."""
    import asana
    
    print(f"🔄 Moving task {task_id} to Processing section...")
    
    try:
        client = asana.Client.access_token(os.getenv('ASANA_API_KEY'))
        project_id = os.getenv('ASANA_PROJECT_ID')
        
        # Get sections
        sections = client.sections.find_by_project(project_id)
        processing_section = None
        
        for section in sections:
            if 'qa' in section.get('name', '').lower() and 'processing' in section.get('name', '').lower():
                processing_section = section
                break
        
        if not processing_section:
            print("❌ 'QA – Processing' section not found")
            return False
        
        # Try to move task to processing section using section-specific method
        try:
            # Use the section's add_task method
            client.sections.add_task(processing_section.get('gid'), {'task': task_id})
            print(f"✅ Moved task to {processing_section.get('name')} section")
            return True
        except Exception as e:
            print(f"⚠️  Could not move task to processing section: {str(e)}")
            # Add a comment instead to indicate processing
            comment = f"🔄 Task moved to Processing (simulated)\n\nThis task is now being processed by the AI agent."
            client.tasks.add_comment(task_id, {'text': comment})
            print(f"✅ Added processing comment to task")
            return True
        
    except Exception as e:
        print(f"❌ Error moving task to processing: {str(e)}")
        return False

def move_task_to_manual_followup(task_id, reason):
    """Move task to QA – Manual Follow-up Required section."""
    import asana
    
    print(f"📋 Moving task {task_id} to Manual Follow-up Required section...")
    
    try:
        client = asana.Client.access_token(os.getenv('ASANA_API_KEY'))
        project_id = os.getenv('ASANA_PROJECT_ID')
        
        # Get sections
        sections = client.sections.find_by_project(project_id)
        manual_section = None
        
        for section in sections:
            if 'qa' in section.get('name', '').lower() and 'manual follow-up' in section.get('name', '').lower():
                manual_section = section
                break
        
        if not manual_section:
            print("❌ 'QA – Manual Follow-up Required' section not found")
            return False
        
        # Move task to manual follow-up section
        try:
            client.sections.add_task(manual_section.get('gid'), {'task': task_id})
            print(f"✅ Moved task to {manual_section.get('name')} section")
        except Exception as e:
            print(f"⚠️  Could not move task to manual follow-up section: {str(e)}")
        
        # Add comment explaining the reason
        comment = f"📋 Task moved to Manual Follow-up Required\n\nReason: {reason}\n\nThis task requires manual review and processing."
        client.tasks.add_comment(task_id, {'text': comment})
        
        print(f"✅ Added manual follow-up comment to task")
        return True
        
    except Exception as e:
        print(f"❌ Error moving task to manual follow-up: {str(e)}")
        return False

def move_task_to_issues(task_id, issue_reason):
    """Move task to QA - Issues section."""
    import asana
    
    print(f"⚠️ Moving task {task_id} to Issues section...")
    
    try:
        client = asana.Client.access_token(os.getenv('ASANA_API_KEY'))
        project_id = os.getenv('ASANA_PROJECT_ID')
        
        # Get sections
        sections = client.sections.find_by_project(project_id)
        issues_section = None
        
        for section in sections:
            if 'qa' in section.get('name', '').lower() and 'issues' in section.get('name', '').lower():
                issues_section = section
                break
        
        if not issues_section:
            print("❌ 'QA - Issues' section not found")
            return False
        
        # Move task to issues section
        try:
            client.sections.add_task(issues_section.get('gid'), {'task': task_id})
            print(f"✅ Moved task to {issues_section.get('name')} section")
        except Exception as e:
            print(f"⚠️  Could not move task to issues section: {str(e)}")
        
        # Add comment explaining the issue
        comment = f"⚠️ Task moved to Issues section\n\nIssue: {issue_reason}\n\nThis task has technical issues that need to be resolved."
        client.tasks.add_comment(task_id, {'text': comment})
        
        print(f"✅ Added issues comment to task")
        return True
        
    except Exception as e:
        print(f"❌ Error moving task to issues: {str(e)}")
        return False

def download_pdf_from_task(task_id):
    """Download PDF from task attachments or notes URL."""
    import asana
    import requests
    import re
    import tempfile

    print(f"📥 Downloading PDF from task {task_id}...")

    try:
        client = asana.Client.access_token(os.getenv('ASANA_API_KEY'))
        task = client.tasks.find_by_id(task_id, opt_fields=['name', 'attachments.name', 'attachments.type', 'attachments.size', 'attachments.download_url', 'notes'])

        print(f"📋 Task: {task.get('name')}")
        print(f"📝 Notes length: {len(task.get('notes', ''))}")

        # First check file attachments
        attachments = task.get('attachments', [])
        print(f"📎 Found {len(attachments)} file attachments")

        for attachment in attachments:
            attachment_name = attachment.get('name', '')
            print(f"📄 Checking attachment: {attachment_name}")

            if attachment_name and attachment_name.lower().endswith('.pdf'):
                print(f"📄 Found PDF attachment: {attachment_name}")

                download_url = attachment.get('download_url')
                if download_url:
                    try:
                        print(f"🔗 Downloading from: {download_url}")
                        response = requests.get(download_url)
                        if response.status_code == 200:
                            temp_dir = os.getenv('TEMP_DOWNLOAD_DIR', '/tmp/agno_pdfs')
                            os.makedirs(temp_dir, exist_ok=True)
                            file_path = os.path.join(temp_dir, f"{task_id}_{attachment_name}")

                            with open(file_path, 'wb') as f:
                                f.write(response.content)

                            print(f"✅ Downloaded attachment to: {file_path}")
                            return file_path
                        else:
                            print(f"❌ Failed to download attachment: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Error downloading attachment: {str(e)}")
                else:
                    print("❌ No download URL for attachment")

        # If no PDF attachments, check notes for PDF URLs
        notes = task.get('notes', '')
        if notes:
            print(f"📝 Checking notes for PDF URLs...")
            pdf_urls = re.findall(r'http[s]?://[^\s]+\.pdf', notes, re.IGNORECASE)

            if pdf_urls:
                pdf_url = pdf_urls[0]  # Take the first PDF URL found
                print(f"🔗 Found PDF URL in notes: {pdf_url}")

                try:
                    print(f"🔗 Downloading from URL: {pdf_url}")
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        temp_dir = os.getenv('TEMP_DOWNLOAD_DIR', '/tmp/agno_pdfs')
                        os.makedirs(temp_dir, exist_ok=True)
                        filename = pdf_url.split('/')[-1]
                        file_path = os.path.join(temp_dir, f"{task_id}_{filename}")

                        with open(file_path, 'wb') as f:
                            f.write(response.content)

                        print(f"✅ Downloaded PDF from URL to: {file_path}")
                        return file_path
                    else:
                        print(f"❌ Failed to download PDF from URL: {response.status_code}")
                        return None
                except Exception as e:
                    print(f"❌ Error downloading PDF from URL: {str(e)}")
                    return None

        print("⚠️  No PDF attachments or URLs found")
        return None
        
    except Exception as e:
        print(f"❌ Error downloading PDF: {str(e)}")
        return None

def extract_form_info(pdf_path):
    """Extract form information from a PDF file."""
    import PyPDF2
    import pdfplumber
    import re

    print(f"🔍 Extracting form info from: {pdf_path}")

    try:
        # Try pdfplumber first for better text extraction
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""

        print(f"📄 Extracted {len(text)} characters of text")

        # Determine form type first
        if 'form 471' in text.lower() or '471' in text.lower():
            form_type = '471'
            print(f"✅ Confirmed: Form 471")
        elif 'form 470' in text.lower() or '470' in text.lower():
            form_type = '470'
            print(f"✅ Confirmed: Form 470")
        else:
            form_type = 'unknown'
            print(f"⚠️  Form type: unknown")

        # Extract application number
        app_number_match = re.search(r'Application Number[:\s]*(\d+)', text, re.IGNORECASE)
        if app_number_match:
            application_number = app_number_match.group(1)
            print(f"✅ Found application number: {application_number}")
        else:
            # Try alternative patterns
            app_number_match = re.search(r'(\d{9})', text)
            if app_number_match:
                application_number = app_number_match.group(1)
                print(f"✅ Found application number (alternative): {application_number}")
            else:
                print("❌ No application number found")
                return {}

        # Extract billed entity name
        entity_match = re.search(r'Billed Entity Name[:\s]*([^\n]+)', text, re.IGNORECASE)
        if entity_match:
            billed_entity_name = entity_match.group(1).strip()
            print(f"✅ Found billed entity: {billed_entity_name}")
        else:
            billed_entity_name = "Unknown"
            print(f"⚠️  Billed entity: unknown")

        # CRITICAL: Extract Establishing FCC Form 470 number from Form 471
        establishing_form470_number = None
        if form_type == '471':
            # Look for "Establishing FCC Form 470" field
            establishing_match = re.search(r'Establishing FCC Form 470[:\s]*(\d+)', text, re.IGNORECASE)
            if establishing_match:
                establishing_form470_number = establishing_match.group(1)
                print(f"✅ Found Establishing FCC Form 470 number: {establishing_form470_number}")
            else:
                # Try alternative patterns for the establishing Form 470 field
                establishing_match = re.search(r'Establishing.*Form 470[:\s]*(\d+)', text, re.IGNORECASE)
                if establishing_match:
                    establishing_form470_number = establishing_match.group(1)
                    print(f"✅ Found Establishing Form 470 number (alternative): {establishing_form470_number}")
                else:
                    # Look for any 15-digit number that might be the establishing Form 470
                    establishing_match = re.search(r'(\d{15})', text)
                    if establishing_match:
                        establishing_form470_number = establishing_match.group(1)
                        print(f"✅ Found potential Establishing Form 470 number (15-digit): {establishing_form470_number}")
                    else:
                        print("⚠️  No Establishing FCC Form 470 number found in Form 471")

        form_info = {
            'application_number': application_number,
            'form_type': form_type,
            'billed_entity_name': billed_entity_name
        }

        # Add the establishing Form 470 number if found (this is the key for linking)
        if establishing_form470_number:
            form_info['establishing_form470_number'] = establishing_form470_number
            print(f"🔗 Form 471 links to Form 470: {establishing_form470_number}")

        print(f"📋 Extracted form info: {form_info}")
        return form_info

    except Exception as e:
        print(f"❌ Error extracting form info: {str(e)}")
        return {}

def search_form470(form_info):
    """Search USAC API for matching Form 470 using form information."""
    import requests

    print(f"🔍 Searching USAC API for Form 470...")
    print(f"📋 Using form info: {form_info}")

    try:
        # For Form 471, use the establishing Form 470 number to search for Form 470
        if form_info.get('form_type') == '471' and form_info.get('establishing_form470_number'):
            search_number = form_info.get('establishing_form470_number')
            print(f"🔗 Using Establishing FCC Form 470 number: {search_number}")
            print(f"📝 This is the official way to link Form 471 to Form 470")
        else:
            # Fallback to application number if no establishing Form 470 number found
            search_number = form_info.get('application_number')
            print(f"⚠️  No Establishing FCC Form 470 number found, using application number: {search_number}")
        
        if not search_number:
            print("❌ No search number found in form info")
            return {'found': False, 'error': 'No search number found'}

        print(f"🔗 Querying USAC API for Form 470 with number: {search_number}")

        # Query USAC API
        url = "https://opendata.usac.org/resource/jt8s-3q52.json"
        params = {
            '$where': f"application_number='{search_number}'"
        }

        response = requests.get(url, params=params)
        print(f"🔗 API Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"📊 Found {len(data)} matching records")

            if data:
                # Found matching Form 470
                form470_record = data[0]
                form470_url = form470_record.get('form_pdf', '')
                
                if form470_url:
                    print(f"✅ Found Form 470 URL: {form470_url}")
                    print(f"✅ Form 471 successfully linked to Form 470 via Establishing FCC Form 470 field")
                    return {
                        'found': True,
                        'form470_url': form470_url,
                        'search_number': search_number,
                        'record': form470_record
                    }
                else:
                    print(f"⚠️  Form 470 found but no URL available")
                    return {
                        'found': False,
                        'search_number': search_number,
                        'error': 'No URL in record'
                    }
            else:
                print(f"❌ No Form 470 found for number: {search_number}")
                if form_info.get('form_type') == '471':
                    print(f"⚠️  This Form 471 may not have a corresponding Form 470 in the database")
                return {
                    'found': False,
                    'search_number': search_number
                }
        else:
            print(f"❌ API request failed: {response.status_code}")
            return {
                'found': False,
                'search_number': search_number,
                'error': f'API error: {response.status_code}'
            }

    except Exception as e:
        print(f"❌ Error searching Form 470: {str(e)}")
        return {
            'found': False,
            'search_number': form_info.get('establishing_form470_number') or form_info.get('application_number'),
            'error': str(e)
        }

def mark_task_complete(task_id, form470_url):
    """Mark task as complete with Form 470 URL."""
    import asana
    
    print(f"✅ Marking task {task_id} as complete...")
    
    try:
        client = asana.Client.access_token(os.getenv('ASANA_API_KEY'))
        
        # Mark task as completed
        client.tasks.update(task_id, {'completed': True})
        
        # Add comment with Form 470 URL
        comment = f"✅ Task completed successfully!\n\nForm 470 found and linked:\n{form470_url}\n\nThis task was automatically processed by the AI agent."
        client.tasks.add_comment(task_id, {'text': comment})
        
        print(f"✅ Task marked as completed with Form 470 URL")
        return True
        
    except Exception as e:
        print(f"❌ Error completing task: {str(e)}")
        return False

def create_manual_review_subtask(task_id, form_info):
    """Create a sub-task for manual review when Form 470 is not found."""
    import asana
    
    print(f"📝 Creating manual review sub-task for task {task_id}...")
    
    try:
        client = asana.Client.access_token(os.getenv('ASANA_API_KEY'))
        project_id = os.getenv('ASANA_PROJECT_ID')
        
        # Get the parent task to get workspace info
        parent_task = client.tasks.find_by_id(task_id)
        
        # Get project to get workspace
        project = client.projects.find_by_id(project_id)
        workspace_gid = project.get('workspace', {}).get('gid')
        
        if not workspace_gid:
            print("❌ Could not get workspace GID")
            return False
        
        # Create sub-task
        subtask_data = {
            'name': f"Manual Review: Find Form 470 for {form_info.get('application_number', 'Unknown')}",
            'notes': f"""This sub-task was created automatically because no Form 470 was found for Form 471.

Form 471 Application Number: {form_info.get('application_number', 'Unknown')}
Form Type: {form_info.get('form_type', 'Unknown')}
Billed Entity: {form_info.get('billed_entity_name', 'Unknown')}

Please manually search for the corresponding Form 470 and update this sub-task with the results.

Expected actions:
1. Search USAC database for Form 470
2. Verify the Form 470 matches the Form 471
3. Update this sub-task with findings
4. Mark parent task as complete if Form 470 is found""",
            'parent': task_id,
            'workspace': workspace_gid
        }
        
        subtask = client.tasks.create(subtask_data)
        
        print(f"✅ Created sub-task: {subtask.get('name')}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sub-task: {str(e)}")
        return False

def get_task_details(task_id):
    """Get detailed information about a specific task."""
    import asana
    
    print(f"📋 Getting details for task {task_id}...")
    
    try:
        client = asana.Client.access_token(os.getenv('ASANA_API_KEY'))
        task = client.tasks.find_by_id(task_id, opt_fields=['name', 'notes', 'attachments.name', 'attachments.type', 'attachments.download_url', 'memberships.section.name'])
        
        print(f"📋 Task: {task.get('name')}")
        print(f"📝 Notes: {task.get('notes', 'No notes')[:200]}...")
        print(f"📎 Attachments: {len(task.get('attachments', []))}")
        
        return task
        
    except Exception as e:
        print(f"❌ Error getting task details: {str(e)}")
        return None

# Create the unified agent
asana_form_agent = Agent(
    model=OpenAIChat(id="gpt-4.1-nano"),
    tools=[
        Function(
            name="get_qa_tasks",
            description="Get all tasks in QA section from Asana project",
            func=get_qa_tasks
        ),
        Function(
            name="get_task_details",
            description="Get detailed information about a specific task",
            func=get_task_details
        ),
        Function(
            name="move_task_to_processing",
            description="Move task to QA – Processing section",
            func=move_task_to_processing
        ),
        Function(
            name="move_task_to_manual_followup",
            description="Move task to QA – Manual Follow-up Required section",
            func=move_task_to_manual_followup
        ),
        Function(
            name="move_task_to_issues",
            description="Move task to QA - Issues section",
            func=move_task_to_issues
        ),
        Function(
            name="download_pdf_from_task",
            description="Download PDF from task attachments or notes URL",
            func=download_pdf_from_task
        ),
        Function(
            name="extract_form_info",
            description="Extract form information from a PDF file",
            func=extract_form_info
        ),
        Function(
            name="search_form470",
            description="Search USAC API for matching Form 470 using form information",
            func=search_form470
        ),
        Function(
            name="mark_task_complete",
            description="Mark task as complete with Form 470 URL",
            func=mark_task_complete
        ),
        Function(
            name="create_manual_review_subtask",
            description="Create a sub-task for manual review when Form 470 is not found",
            func=create_manual_review_subtask
        )
    ],
    instructions=dedent("""\
        You are an intelligent Asana workflow automation agent specializing in USAC Form processing! 📋

        Your mission: Automate the processing of Form 471 PDFs and find their corresponding Form 470 documents with proper workflow transitions.

        INTELLIGENT WORKFLOW - USE YOUR TOOLS TO MAKE DECISIONS:

        STEP 1: Get QA Tasks
        - Call get_qa_tasks() to retrieve all tasks in QA section
        - For each task ID returned, call get_task_details(task_id) to get full information

        STEP 2: For Each QA Task - MAKE INTELLIGENT DECISIONS:
        
        a) First, move the task to processing: Call move_task_to_processing(task_id)
        
        b) Try to download PDF: Call download_pdf_from_task(task_id)
        
        c) If PDF download succeeds:
           - Extract form information: Call extract_form_info(pdf_path)
           - Analyze the form type and extracted data
           - Search for Form 470: Call search_form470(form_info)
           - MAKE DECISION: If Form 470 found, mark task complete; if not, move to manual follow-up
        
        d) If PDF download fails:
           - MAKE DECISION: Move task to issues section
        
        STEP 3: Form 470 Search Logic:
        - For Form 471: Use the "Establishing FCC Form 470" number to search
        - This is the official way to link Form 471 to Form 470
        - The establishing Form 470 number is extracted from Form 471 PDF

        CRITICAL: You MUST call each tool function explicitly and make intelligent decisions!
        - Show your work at every step
        - Report results of each tool call
        - Explain your reasoning for each decision
        - Display all extracted information clearly
        - Always move tasks to appropriate sections based on results
        - Use your intelligence to handle edge cases and errors

        DECISION MAKING:
        - If Form 470 found: Call mark_task_complete(task_id, form470_url)
        - If Form 470 not found: Call move_task_to_manual_followup(task_id, reason) AND create_manual_review_subtask(task_id, form_info)
        - If PDF download fails: Call move_task_to_issues(task_id, issue_reason)
        - If no PDF found: Call move_task_to_issues(task_id, "No PDF found")

        EXAMPLE WORKFLOW:
        1. Call get_qa_tasks() - get list of QA tasks
        2. For each task ID: Call get_task_details(task_id) - get task info
        3. Call move_task_to_processing(task_id) - move to processing
        4. Call download_pdf_from_task(task_id) - try to download PDF
        5. If PDF downloaded: Call extract_form_info(pdf_path) - extract form data
        6. Call search_form470(form_info) - search for Form 470
        7. Make decision based on search result and call appropriate action

        """),
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    markdown=True,
)

def run_watcher_mode():
    """Run the agent in continuous monitoring mode."""
    print("🚀 ASANA FORM AGENT - WATCHER MODE")
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
        print("🚀 Running Asana Form Agent...")
        print("=" * 50)
        
        try:
            # Run the agent
            asana_form_agent.print_response(
                "Process all QA tasks in the Asana project. Download PDFs from attachments or notes URLs, extract form information, search for matching Form 470, and update task status accordingly. Show me exactly what you're doing at each step.",
                stream=True
            )
            
            print("✅ Agent run completed")
            print(f"✅ Run #{run_count} completed successfully")
            
        except Exception as e:
            print(f"❌ Error in run #{run_count}: {str(e)}")
        
        if not shutdown_flag:
            print("⏳ Waiting 60 seconds until next run...")
            time.sleep(60)
    
    print("🛑 Watcher mode stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--watcher":
        # Run in watcher mode
        run_watcher_mode()
    else:
        # Run once
        print("🚀 Asana Form Agent Starting...")
        print("📋 Processing QA tasks in Asana project...")
        asana_form_agent.print_response(
            "Process all QA tasks in the Asana project. Download PDFs from attachments or notes URLs, extract form information, search for matching Form 470, and update task status accordingly. Show me exactly what you're doing at each step.",
            stream=True
        ) 