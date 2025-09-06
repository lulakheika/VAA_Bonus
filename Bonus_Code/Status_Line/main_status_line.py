#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Status Line Implementation for Claude Code

Author: Russo Davide (The DaveEloper)
Email: vibecoding@pcok.it
Project: ChatTokener Suite
Component: VAA Bonus - Status Line
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# def log_status_line(input_data, status_line_output, error=None):
#     """Log status line event to logs directory."""
#     # Ensure logs directory exists
#     log_dir = Path("logs")
#     log_dir.mkdir(parents=True, exist_ok=True)
#     log_file = log_dir / 'status_line.json'
#     
#     # Read existing log data or initialize empty list
#     if log_file.exists():
#         with open(log_file, 'r') as f:
#             try:
#                 log_data = json.load(f)
#             except (json.JSONDecodeError, ValueError):
#                 log_data = []
#     else:
#         log_data = []
#     
#     # Create log entry with input data and generated output
#     log_entry = {
#         "timestamp": datetime.now().isoformat(),
#         "input_data": input_data,
#         "status_line_output": status_line_output
#     }
#     
#     if error:
#         log_entry["error"] = str(error)
#     
#     # Append the log entry
#     log_data.append(log_entry)
#     
#     # Write back to file with formatting
#     with open(log_file, 'w') as f:
#         json.dump(log_data, f, indent=2, default=str)


def get_git_branch():
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            timeout=1,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def format_cost(cost):
    """Format cost value with appropriate precision."""
    if cost == 0:
        return "$0.00"
    elif cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1:
        return f"${cost:.3f}"
    else:
        return f"${cost:.2f}"


def create_progress_bar(percentage, length=10):
    """Create a visual progress bar."""
    filled = int((percentage / 100) * length)
    bar = "█" * filled + "░" * (length - filled)
    return bar


def get_context_color(percentage):
    """Get color code based on context usage percentage."""
    if percentage < 50:
        return "\033[32m"  # Green
    elif percentage < 75:
        return "\033[33m"  # Yellow
    elif percentage < 90:
        return "\033[91m"  # Light Red
    else:
        return "\033[31m"  # Red


def get_session_data(session_id):
    """Get session data including prompts from session file."""
    session_file = Path(f".claude/data/sessions/{session_id}.json")
    
    if not session_file.exists():
        return None
    
    try:
        with open(session_file, "r") as f:
            session_data = json.load(f)
            return session_data
    except Exception:
        return None


def count_messages_in_transcript(transcript_path, session_id):
    """Count total user and assistant messages in the transcript."""
    if not transcript_path or not Path(transcript_path).exists():
        return 0, 0
    
    user_count = 0
    assistant_count = 0
    
    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Skip if different session ID  
                    if session_id and entry.get('sessionId') and entry.get('sessionId') != session_id:
                        continue
                    
                    entry_type = entry.get('type')
                    if entry_type == 'user' and not entry.get('isMeta'):
                        user_count += 1
                    elif entry_type == 'assistant':
                        # Only count assistant messages with actual content
                        message = entry.get('message', {})
                        if message.get('usage') or message.get('content'):
                            assistant_count += 1
                            
                except (json.JSONDecodeError, Exception):
                    continue
    except Exception:
        pass
    
    return user_count, assistant_count


def get_execution_time_from_transcript(transcript_path, session_id):
    """Get execution time of last assistant response and total session time."""
    if not transcript_path or not Path(transcript_path).exists():
        return None, None
    
    first_timestamp = None
    last_timestamp = None
    last_response_time = None
    
    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Skip if different session ID
                    if session_id and entry.get('sessionId') and entry.get('sessionId') != session_id:
                        continue
                    
                    # Get timestamps
                    timestamp = entry.get('timestamp')
                    if timestamp:
                        if not first_timestamp:
                            first_timestamp = timestamp
                        last_timestamp = timestamp
                    
                    # Track assistant response time (could be in metadata)
                    if entry.get('type') == 'assistant':
                        metadata = entry.get('metadata', {})
                        if 'response_time' in metadata:
                            last_response_time = metadata['response_time']
                            
                except (json.JSONDecodeError, Exception):
                    continue
                    
        # Calculate session duration
        session_duration = None
        if first_timestamp and last_timestamp:
            try:
                from datetime import datetime
                first = datetime.fromisoformat(first_timestamp.replace('Z', '+00:00'))
                last = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                duration_seconds = (last - first).total_seconds()
                if duration_seconds > 0:
                    session_duration = duration_seconds
            except:
                pass
                
    except Exception:
        pass
    
    return last_response_time, session_duration


def format_duration(seconds):
    """Format duration in seconds to human readable format."""
    if seconds is None:
        return None
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_real_token_usage(input_data):
    """
    Parse last exchange token usage and first user message from transcript.
    Returns dict with total_tokens and first_message, or None if parsing fails.
    """
    transcript_path = input_data.get('transcript_path')
    if not transcript_path or not Path(transcript_path).exists():
        return None
    
    session_id = input_data.get('session_id')
    last_usage = None
    first_user_message = None
    
    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Capture first user message (skip meta messages and wrong sessions)
                    if not first_user_message and entry.get('type') == 'user' and not entry.get('isMeta'):
                        # Must match session ID or be the very first message (parentUuid is null)
                        if (session_id and entry.get('sessionId') == session_id) or entry.get('parentUuid') is None:
                            message = entry.get('message', {})
                            if message.get('role') == 'user':
                                content = message.get('content')
                                if isinstance(content, str):
                                    first_user_message = content
                                elif isinstance(content, list) and len(content) > 0:
                                    # Extract text from content array
                                    for item in content:
                                        if isinstance(item, dict) and item.get('type') == 'text':
                                            text = item.get('text', '')
                                            # Clean up the message
                                            if text and not text.startswith('<command'):
                                                # Remove leading pipe and arrow if present
                                                text = text.lstrip('│ > ').lstrip('> ')
                                                first_user_message = text
                                                break
                    
                    # Only look at assistant messages from main session
                    if entry.get('type') == 'assistant':
                        # Skip if different session ID
                        if session_id and entry.get('sessionId') != session_id:
                            continue
                            
                        message = entry.get('message', {})
                        usage = message.get('usage', {})
                        
                        # Only consider messages with actual token usage
                        if usage and (usage.get('input_tokens', 0) > 0 or 
                                     usage.get('cache_creation_input_tokens', 0) > 0 or
                                     usage.get('output_tokens', 0) > 0):
                            last_usage = usage
                            
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue
    
    except Exception:
        return None
    
    if not last_usage:
        return None
    
    # Calculate totals for the last exchange
    input_tokens = last_usage.get('input_tokens', 0)
    cache_read = last_usage.get('cache_read_input_tokens', 0)
    cache_creation = last_usage.get('cache_creation_input_tokens', 0)
    output_tokens = last_usage.get('output_tokens', 0)
    
    # Total tokens processed (all of them fill Claude's head)
    total_tokens = input_tokens + cache_creation + cache_read + output_tokens
    
    return {
        "total_tokens": total_tokens,
        "first_message": first_user_message,
        "breakdown": {
            "direct_input": input_tokens,
            "cache_read": cache_read,
            "cache_creation": cache_creation,
            "output": output_tokens
        },
        "cache_efficiency": {
            "cache_hit_ratio": round(cache_read / (cache_read + input_tokens + cache_creation) * 100, 1) if (cache_read + input_tokens + cache_creation) > 0 else 0,
            "cache_tokens_saved": cache_read
        }
    }


def generate_status_line(input_data):
    """Generate status line with costs and context window usage."""
    parts = []
    
    # Model name
    model_info = input_data.get('model', {})
    model_name = model_info.get('display_name', 'Claude')
    parts.append(f"\033[36m[{model_name}]\033[0m")  # Cyan
    
    # Get session data for prompts
    session_id = input_data.get('session_id', '')
    session_data = get_session_data(session_id) if session_id else None
    
    # Message counter
    transcript_path = input_data.get('transcript_path')
    user_count, assistant_count = count_messages_in_transcript(transcript_path, session_id)
    if user_count > 0 or assistant_count > 0:
        parts.append(f"\033[95m💬 {user_count}/{assistant_count}\033[0m")  # Magenta
    
    # Todo list status (if todos are present in input_data)
    todos = input_data.get('todos', [])
    if todos:
        completed = sum(1 for t in todos if t.get('status') == 'completed')
        total = len(todos)
        # Color based on completion
        if completed == total:
            todo_color = "\033[32m"  # Green - all done
        elif completed > total / 2:
            todo_color = "\033[33m"  # Yellow - more than half done
        else:
            todo_color = "\033[91m"  # Light Red - less than half done
        parts.append(f"{todo_color}📝 {completed}/{total}\033[0m")
    
    # Git branch (if available)
    git_branch = get_git_branch()
    if git_branch:
        parts.append(f"\033[32m🌿 {git_branch}\033[0m")  # Green
    
    # Session costs - Extract from the cost field
    cost_data = input_data.get('cost', {})
    session_cost = cost_data.get('total_cost_usd', 0)
    
    # Format and add cost
    if session_cost > 0:
        cost_str = format_cost(session_cost)
        parts.append(f"\033[33m💰 {cost_str}\033[0m")  # Yellow
    else:
        parts.append(f"\033[90m💰 $0.00\033[0m")  # Gray
    
    # Context window usage - try to get real tokens first
    exceeds_200k = input_data.get('exceeds_200k_tokens', False)
    
    # Set context window based on model
    model_id = model_info.get('id', '')
    if 'opus' in model_id.lower():
        context_window = 200000
        avg_rate = 30  # For fallback estimation
    elif 'sonnet' in model_id.lower():
        context_window = 200000
        avg_rate = 6
    elif 'haiku' in model_id.lower():
        context_window = 200000
        avg_rate = 0.5
    else:
        context_window = 200000
        avg_rate = 6
    
    # Try to get real token usage from transcript
    token_data = get_real_token_usage(input_data)
    
    if token_data and token_data.get('total_tokens'):
        # Use TOTAL tokens processed (including cache) - this is what fills Claude's head!
        tokens_used = token_data['total_tokens']  # The full 149k, not just the 778 new ones
        
        # Add first message preview if available
        first_msg = token_data.get('first_message')
        if first_msg:
            # Truncate at first backslash or § if present
            backslash_pos = first_msg.find('\\')
            section_pos = first_msg.find('§')
            
            # Find the earliest delimiter position
            delimiter_positions = [pos for pos in [backslash_pos, section_pos] if pos != -1]
            if delimiter_positions:
                first_delimiter = min(delimiter_positions)
                first_msg = first_msg[:first_delimiter]
            
            # Clean the message for display
            first_msg = first_msg.replace('\n', ' ').replace('\r', '')
            parts.append(f"\033[95m💬 {first_msg}\033[0m")  # Magenta for message
    else:
        # Fallback to estimation from cost
        if session_cost > 0 and avg_rate > 0:
            tokens_used = int((session_cost * 1_000_000) / avg_rate)
        else:
            tokens_used = 0
    
    # If we exceed 200k, show as 100%
    if exceeds_200k:
        tokens_used = max(tokens_used, context_window)
    
    # Calculate percentage
    if context_window > 0:
        usage_percentage = min(100, int((tokens_used / context_window) * 100))
    else:
        usage_percentage = 0
    
    # Create visual representation
    progress_bar = create_progress_bar(usage_percentage)
    color = get_context_color(usage_percentage)
    
    # Format token display
    if tokens_used >= 1000:
        tokens_display = f"{tokens_used/1000:.1f}k"
    else:
        tokens_display = str(tokens_used)
    
    if context_window >= 1000:
        context_display = f"{context_window//1000}k"
    else:
        context_display = str(context_window)
    
    # Add context window usage with color-coded bar
    context_str = f"{color}[{progress_bar}] {usage_percentage}% ({tokens_display}/{context_display})\033[0m"
    parts.append(f"📊 {context_str}")
    
    # Session info (optional)
    session_id = input_data.get('session_id', '')
    if session_id:
        # Show shortened session ID
        short_id = session_id[:8] if len(session_id) > 8 else session_id
        parts.append(f"\033[90m#{short_id}\033[0m")  # Gray
    
    # Execution time
    last_response_time, session_duration = get_execution_time_from_transcript(transcript_path, session_id)
    if session_duration:
        duration_str = format_duration(session_duration)
        parts.append(f"\033[94m⏱️ {duration_str}\033[0m")  # Light Blue
    
    # Current time (optional, useful for tracking session duration)
    current_time = datetime.now().strftime("%H:%M")
    parts.append(f"\033[90m⏰ {current_time}\033[0m")  # Gray
    
    return " | ".join(parts)


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Generate status line
        status_line = generate_status_line(input_data)
        
        # Log the status line event
        # log_status_line(input_data, status_line)
        
        # Output the status line
        print(status_line)
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse JSON input: {e}"
        fallback_status = "\033[31m[Error]\033[0m Failed to parse status data"
        # log_status_line({}, fallback_status, error_msg)
        print(fallback_status)
    except Exception as e:
        error_msg = f"Status line error: {e}"
        fallback_status = "\033[31m[Error]\033[0m Status line generation failed"
        # log_status_line({}, fallback_status, error_msg)
        print(fallback_status)


if __name__ == '__main__':
    main()