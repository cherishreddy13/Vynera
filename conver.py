# app.py
from flask import Flask, render_template_string, jsonify, request, send_file
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
import json
import re
from io import BytesIO

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://reddycherish76:Cherish1302@dataleak.zr189.mongodb.net/')
client = MongoClient(MONGO_URI)
db = client['vynera']
conversations_collection = db['conversations']
users_collection = db['users']
feedback_collection = db['feedback']
goals_collection = db['goal']
journals_collection = db['journals']
memories_collection = db['memories']

def force_clean_text(text):
    """Forcefully remove any invalid Unicode characters"""
    if text is None:
        return ''
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return ''
    
    try:
        return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    except:
        pass
    
    try:
        result = []
        for char in text:
            code = ord(char)
            if 0xD800 <= code <= 0xDFFF:
                result.append('?')
            else:
                result.append(char)
        return ''.join(result)
    except:
        return text.encode('ascii', errors='ignore').decode('ascii', errors='ignore')

def deep_clean(obj):
    """Recursively clean all strings in an object"""
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            clean_key = force_clean_text(key) if isinstance(key, str) else str(key)
            cleaned[clean_key] = deep_clean(value)
        return cleaned
    elif isinstance(obj, list):
        return [deep_clean(item) for item in obj]
    elif isinstance(obj, str):
        return force_clean_text(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        try:
            if obj is None:
                return None
            if isinstance(obj, (int, float, bool)):
                return obj
            return force_clean_text(str(obj))
        except:
            return None

def convert_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    
    doc = dict(doc)
    
    if '_id' in doc and isinstance(doc['_id'], ObjectId):
        doc['_id'] = str(doc['_id'])
    if 'user_id' in doc and isinstance(doc['user_id'], ObjectId):
        doc['user_id'] = str(doc['user_id'])
    if 'conv_id' in doc and isinstance(doc['conv_id'], ObjectId):
        doc['conv_id'] = str(doc['conv_id'])
    
    if 'created_at' in doc and isinstance(doc['created_at'], datetime):
        doc['created_at'] = doc['created_at'].isoformat()
    if 'updated_at' in doc and isinstance(doc['updated_at'], datetime):
        doc['updated_at'] = doc['updated_at'].isoformat()
    
    if 'messages' in doc and isinstance(doc['messages'], list):
        for msg in doc['messages']:
            if isinstance(msg, dict):
                if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
                    msg['timestamp'] = msg['timestamp'].isoformat()
    
    cleaned_doc = deep_clean(doc)
    return cleaned_doc

def generate_selected_md_file(selected_conversations, users_map):
    """Generate markdown file for selected conversations"""
    md_content = []
    
    # Header
    md_content.append("# 🎭 VYNERA Selected Conversations Export")
    md_content.append("")
    md_content.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    md_content.append(f"**Total Selected Conversations:** {len(selected_conversations)}")
    md_content.append("")
    md_content.append("---")
    md_content.append("")
    
    # Group conversations by user
    conversations_by_user = {}
    for conv in selected_conversations:
        user_id = conv.get('user_id', 'unknown')
        if user_id not in conversations_by_user:
            conversations_by_user[user_id] = []
        conversations_by_user[user_id].append(conv)
    
    # Table of Contents
    md_content.append("## 📑 Table of Contents")
    md_content.append("")
    for idx, (user_id, user_convos) in enumerate(conversations_by_user.items(), 1):
        user = users_map.get(user_id, {})
        username = user.get('name', user.get('username', f'User_{user_id[:8]}'))
        anchor = username.lower().replace(' ', '-').replace('@', '').replace('_', '-')
        md_content.append(f"{idx}. [{username}](#{anchor}) - {len(user_convos)} conversation(s)")
    md_content.append("")
    md_content.append("---")
    md_content.append("")
    
    # Export each user's conversations
    for user_id, user_convos in conversations_by_user.items():
        user = users_map.get(user_id, {})
        username = user.get('name', user.get('username', 'Unknown User'))
        anchor = username.lower().replace(' ', '-').replace('@', '').replace('_', '-')
        
        md_content.append(f"## 👤 {username} {{#{anchor}}}")
        md_content.append("")
        
        # User profile summary
        md_content.append("### Profile Summary")
        md_content.append("")
        md_content.append(f"- **Name:** {user.get('name', 'Not provided')}")
        md_content.append(f"- **Username:** @{user.get('username', 'Not provided')}")
        md_content.append(f"- **Personality:** {user.get('personality', 'Not specified')}")
        md_content.append("")
        
        md_content.append(f"### Selected Conversations ({len(user_convos)} total)")
        md_content.append("")
        
        for conv_idx, conv in enumerate(user_convos, 1):
            md_content.append(f"#### Conversation {conv_idx}: {conv.get('title', 'Untitled')}")
            md_content.append("")
            md_content.append(f"- **Topic:** `{conv.get('topic', 'neutral')}`")
            md_content.append(f"- **Conversation ID:** `{conv.get('_id', 'Unknown')}`")
            md_content.append(f"- **Started:** {format_date_md(conv.get('created_at'))}")
            md_content.append(f"- **Last Activity:** {format_date_md(conv.get('updated_at'))}")
            md_content.append(f"- **Total Messages:** {len(conv.get('messages', []))}")
            
            # Mood scores
            mood_scores = conv.get('mood_scores', [])
            if mood_scores:
                md_content.append(f"- **Mood Scores:** {', '.join([str(score) for score in mood_scores[:10]])}")
                if len(mood_scores) > 10:
                    md_content.append(f"  *(+{len(mood_scores) - 10} more)*")
            
            md_content.append("")
            md_content.append("##### Message History")
            md_content.append("")
            
            # Messages
            messages = conv.get('messages', [])
            if messages:
                for msg in messages:
                    role = msg.get('role', 'unknown').upper()
                    content = msg.get('content', '')
                    timestamp = format_date_md(msg.get('timestamp'))
                    
                    md_content.append(f"**{role}** — *{timestamp}*")
                    md_content.append("")
                    content_lines = content.split('\n')
                    for line in content_lines:
                        if line.strip():
                            md_content.append(f"> {line}")
                        else:
                            md_content.append(">")
                    md_content.append("")
                    md_content.append("---")
                    md_content.append("")
            else:
                md_content.append("*No messages in this conversation*")
                md_content.append("")
            
            md_content.append("")
            md_content.append("***")
            md_content.append("")
        
        md_content.append("")
        md_content.append("---")
        md_content.append("")
    
    # Footer
    md_content.append("## 📈 Export Summary")
    md_content.append("")
    total_messages = sum(len(conv.get('messages', [])) for conv in selected_conversations)
    md_content.append(f"- **Export Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    md_content.append(f"- **Selected Conversations:** {len(selected_conversations)}")
    md_content.append(f"- **Total Messages:** {total_messages}")
    md_content.append("")
    md_content.append("---")
    md_content.append(f"*End of Selected Conversations Export*")
    
    return "\n".join(md_content)

def format_date_md(date_string):
    """Format date for markdown display"""
    if not date_string:
        return 'Not recorded'
    try:
        if isinstance(date_string, str):
            date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            date = date_string
        return date.strftime('%B %d, %Y at %I:%M %p')
    except:
        return str(date_string)

# HTML Template with VYNERA Design System and all collections
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>VYNERA — Dashboard</title>
    <style>
        /* ---------- VYNERA DESIGN SYSTEM ---------- */
        
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Reset & Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* SVG Noise Texture */
        .noise-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 100;
            opacity: 0.035;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' /%3E%3C/svg%3E");
            background-repeat: repeat;
            background-size: 200px;
        }
        
        body {
            background: #060606;
            color: #e8e8e0;
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 15px;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
        }
        
        /* Floating Orb Animation */
        .orb {
            position: fixed;
            top: -20%;
            right: -10%;
            width: 600px;
            height: 600px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(201,255,0,0.08) 0%, rgba(201,255,0,0) 70%);
            pointer-events: none;
            z-index: 0;
            animation: floatPulse 8s ease-in-out infinite;
        }
        
        @keyframes floatPulse {
            0%, 100% {
                transform: translate(0, 0) scale(1);
                opacity: 0.5;
            }
            50% {
                transform: translate(-30px, 30px) scale(1.1);
                opacity: 0.7;
            }
        }
        
        /* Fade Up Animation */
        @keyframes fadeUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-up {
            animation: fadeUp 0.5s ease-out forwards;
        }
        
        /* Container */
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 40px 30px;
            position: relative;
            z-index: 2;
        }
        
        /* Typography */
        h1 {
            font-family: 'Bebas Neue', monospace;
            font-size: 80px;
            font-weight: 400;
            letter-spacing: 4px;
            color: #C9FF00;
            margin-bottom: 12px;
            text-transform: uppercase;
            line-height: 1;
        }
        
        .subhead {
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 20px;
            color: #666666;
            font-weight: 400;
            margin-bottom: 40px;
            letter-spacing: 0.3px;
        }
        
        /* Header Actions */
        .header-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 48px;
            flex-wrap: wrap;
            gap: 20px;
            border-bottom: 1px solid #1e1e1c;
            padding-bottom: 24px;
        }
        
        .title-section {
            flex: 1;
        }
        
        /* Button Group */
        .button-group {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 4px;
            background: #0c0c0b;
            padding: 4px;
            border-radius: 60px;
            border: 1px solid #1e1e1c;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .tab-btn {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 500;
            padding: 10px 20px;
            background: transparent;
            border: none;
            color: #666666;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 60px;
            letter-spacing: 0.5px;
        }
        
        .tab-btn.active {
            background: #C9FF00;
            color: #060606;
        }
        
        .tab-btn:hover:not(.active) {
            color: #e8e8e0;
            background: rgba(201,255,0,0.1);
        }
        
        /* Export Buttons */
        .export-btn, .select-export-btn {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 500;
            padding: 10px 24px;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 60px;
            letter-spacing: 0.5px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }
        
        .export-btn {
            background: #C9FF00;
            border: none;
            color: #060606;
        }
        
        .select-export-btn {
            background: transparent;
            border: 1px solid #C9FF00;
            color: #C9FF00;
        }
        
        .export-btn:hover, .select-export-btn:hover {
            background: #b3e600;
            color: #060606;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(201,255,0,0.3);
        }
        
        .select-export-btn:hover {
            background: #C9FF00;
            border-color: #C9FF00;
        }
        
        .export-btn:active, .select-export-btn:active {
            transform: translateY(0);
        }
        
        .export-btn.loading, .select-export-btn.loading {
            opacity: 0.7;
            cursor: wait;
            transform: none;
        }
        
        /* Refresh Button */
        .refresh-btn {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 500;
            padding: 10px 24px;
            background: transparent;
            border: 1px solid #1e1e1c;
            color: #e8e8e0;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 60px;
            letter-spacing: 0.5px;
        }
        
        .refresh-btn:hover {
            border-color: #C9FF00;
            color: #C9FF00;
            box-shadow: 0 0 12px rgba(201,255,0,0.2);
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: #0c0c0b;
            border: 1px solid #1e1e1c;
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            border-color: #C9FF00;
            transform: translateY(-2px);
        }
        
        .stat-number {
            font-family: 'Bebas Neue', monospace;
            font-size: 36px;
            color: #C9FF00;
            line-height: 1;
        }
        
        .stat-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #666666;
            margin-top: 8px;
            letter-spacing: 0.5px;
        }
        
        /* Tab Content */
        .tab-content {
            display: none;
            animation: fadeUp 0.5s ease-out;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Cards Grid */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(460px, 1fr));
            gap: 24px;
        }
        
        /* Card Styling */
        .card {
            background: #0c0c0b;
            border: 1px solid #1e1e1c;
            border-radius: 20px;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .card.selected {
            border-color: #C9FF00;
            box-shadow: 0 0 20px rgba(201,255,0,0.2);
        }
        
        .card:hover {
            border-color: #C9FF00;
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.4);
        }
        
        /* Custom Checkbox Styling */
        .card-checkbox {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 10;
            cursor: pointer;
            width: 24px;
            height: 24px;
        }
        
        .card-checkbox input {
            position: absolute;
            opacity: 0;
            cursor: pointer;
            height: 0;
            width: 0;
        }
        
        .card-checkbox .checkmark {
            position: absolute;
            top: 0;
            left: 0;
            height: 24px;
            width: 24px;
            background-color: #060606;
            border: 2px solid #1e1e1c;
            border-radius: 6px;
            transition: all 0.2s ease;
        }
        
        .card-checkbox:hover input ~ .checkmark {
            border-color: #C9FF00;
            box-shadow: 0 0 8px rgba(201,255,0,0.3);
        }
        
        .card-checkbox input:checked ~ .checkmark {
            background-color: #C9FF00;
            border-color: #C9FF00;
        }
        
        .card-checkbox .checkmark:after {
            content: "";
            position: absolute;
            display: none;
        }
        
        .card-checkbox input:checked ~ .checkmark:after {
            display: block;
        }
        
        .card-checkbox .checkmark:after {
            left: 7px;
            top: 3px;
            width: 6px;
            height: 12px;
            border: solid #060606;
            border-width: 0 2px 2px 0;
            transform: rotate(45deg);
        }
        
        .card-header {
            padding: 20px 60px 16px 24px;
            border-bottom: 1px solid #1e1e1c;
            background: linear-gradient(135deg, #0c0c0b 0%, #0a0a09 100%);
        }
        
        .card-header h3 {
            font-family: 'Bebas Neue', monospace;
            font-size: 24px;
            font-weight: 400;
            letter-spacing: 2px;
            color: #C9FF00;
            margin-bottom: 8px;
            text-transform: uppercase;
            word-break: break-word;
        }
        
        .user-info-badge {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 8px;
            flex-wrap: wrap;
        }
        
        .badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            padding: 4px 12px;
            border-radius: 30px;
            background: rgba(102,102,102,0.15);
            color: #666666;
            letter-spacing: 0.3px;
        }
        
        .badge.positive {
            background: rgba(201,255,0,0.15);
            color: #C9FF00;
        }
        
        .badge.negative {
            background: rgba(255,68,68,0.15);
            color: #ff4444;
        }
        
        .badge.topic {
            background: rgba(201,255,0,0.08);
            color: #C9FF00;
        }
        
        .card-body {
            padding: 20px 24px 24px 24px;
        }
        
        /* Info Rows */
        .info-grid {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .info-row {
            display: flex;
            align-items: flex-start;
            gap: 16px;
            font-size: 13px;
        }
        
        .info-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            min-width: 100px;
        }
        
        .info-value {
            font-family: 'DM Sans', sans-serif;
            color: #e8e8e0;
            word-break: break-word;
            flex: 1;
        }
        
        .info-value.mono {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #666666;
        }
        
        /* Key-Value Pair */
        .key-value-pair {
            background: #060606;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }
        
        .key-value-pair .key {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #C9FF00;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .key-value-pair .value {
            font-family: 'DM Sans', sans-serif;
            color: #e8e8e0;
            word-break: break-word;
        }
        
        /* Mood Scores */
        .mood-section {
            margin: 20px 0;
            padding: 16px;
            background: #0a0a09;
            border-radius: 12px;
            border: 1px solid #1e1e1c;
        }
        
        .mood-title {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            color: #C9FF00;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }
        
        .mood-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .mood-score {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            padding: 4px 10px;
            background: #060606;
            border: 1px solid #1e1e1c;
            border-radius: 30px;
            color: #e8e8e0;
        }
        
        /* Messages Section */
        .messages-section {
            margin-top: 20px;
            border-top: 1px solid #1e1e1c;
            padding-top: 20px;
        }
        
        .messages-title {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            color: #C9FF00;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 8px 16px;
            background: rgba(201,255,0,0.05);
            border-radius: 30px;
            transition: all 0.2s;
            margin-bottom: 16px;
        }
        
        .messages-title:hover {
            background: rgba(201,255,0,0.12);
            gap: 14px;
        }
        
        .messages-list {
            max-height: 360px;
            overflow-y: auto;
            display: none;
            border-radius: 12px;
        }
        
        .messages-list.open {
            display: block;
        }
        
        /* Custom Scrollbar */
        .messages-list::-webkit-scrollbar,
        .conversation-list::-webkit-scrollbar {
            width: 4px;
        }
        
        .messages-list::-webkit-scrollbar-track,
        .conversation-list::-webkit-scrollbar-track {
            background: #1e1e1c;
            border-radius: 4px;
        }
        
        .messages-list::-webkit-scrollbar-thumb,
        .conversation-list::-webkit-scrollbar-thumb {
            background: #C9FF00;
            border-radius: 4px;
        }
        
        /* Message Styling */
        .message {
            padding: 14px 16px;
            margin-bottom: 12px;
            border-radius: 12px;
            font-size: 13px;
            animation: fadeUp 0.3s ease-out;
        }
        
        .message.user {
            background: rgba(201,255,0,0.05);
            border-left: 2px solid #C9FF00;
        }
        
        .message.assistant {
            background: rgba(255,255,255,0.02);
            border-left: 2px solid #666666;
        }
        
        .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .message-role {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 2px 8px;
            border-radius: 4px;
        }
        
        .message.user .message-role {
            color: #C9FF00;
            background: rgba(201,255,0,0.1);
        }
        
        .message.assistant .message-role {
            color: #666666;
            background: rgba(102,102,102,0.15);
        }
        
        .message-timestamp {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #666666;
        }
        
        .message-content {
            font-family: 'DM Sans', sans-serif;
            line-height: 1.5;
            color: #e8e8e0;
            word-break: break-word;
        }
        
        /* Rating Stars */
        .rating-stars {
            font-size: 16px;
            letter-spacing: 2px;
        }
        
        /* Selection Bar */
        .selection-bar {
            background: #0c0c0b;
            border: 1px solid #1e1e1c;
            border-radius: 60px;
            padding: 12px 24px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        
        .selection-info {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #C9FF00;
        }
        
        .selection-actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        
        .selection-btn {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            padding: 6px 16px;
            background: transparent;
            border: 1px solid #1e1e1c;
            color: #e8e8e0;
            cursor: pointer;
            border-radius: 30px;
            transition: all 0.2s;
        }
        
        .selection-btn:hover {
            border-color: #C9FF00;
            color: #C9FF00;
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            backdrop-filter: blur(8px);
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: #0c0c0b;
            border: 1px solid #1e1e1c;
            border-radius: 24px;
            max-width: 650px;
            width: 90%;
            max-height: 85vh;
            overflow: hidden;
            animation: fadeUp 0.3s ease-out;
            display: flex;
            flex-direction: column;
        }
        
        .modal-header {
            padding: 24px;
            border-bottom: 1px solid #1e1e1c;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }
        
        .modal-header h2 {
            font-family: 'Bebas Neue', monospace;
            font-size: 32px;
            color: #C9FF00;
        }
        
        .close-modal {
            font-size: 32px;
            cursor: pointer;
            color: #666666;
            transition: color 0.2s;
            line-height: 1;
        }
        
        .close-modal:hover {
            color: #C9FF00;
        }
        
        .modal-body {
            padding: 24px;
            overflow-y: auto;
            flex: 1;
        }
        
        .modal-footer {
            padding: 20px 24px;
            border-top: 1px solid #1e1e1c;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            flex-shrink: 0;
        }
        
        .filter-group {
            margin-bottom: 20px;
        }
        
        .filter-group label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #666666;
            display: block;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }
        
        .filter-group select, .filter-group input {
            width: 100%;
            padding: 12px;
            background: #060606;
            border: 1px solid #1e1e1c;
            color: #e8e8e0;
            border-radius: 8px;
            font-family: 'DM Sans', sans-serif;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .filter-group select:focus, .filter-group input:focus {
            outline: none;
            border-color: #C9FF00;
        }
        
        .conversation-list {
            max-height: 350px;
            overflow-y: auto;
            margin-top: 16px;
        }
        
        .conversation-item {
            display: flex;
            align-items: flex-start;
            padding: 12px 16px;
            margin-bottom: 8px;
            background: #060606;
            border: 1px solid #1e1e1c;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .conversation-item:hover {
            border-color: #C9FF00;
            background: rgba(201,255,0,0.05);
        }
        
        .conversation-item.selected {
            border-color: #C9FF00;
            background: rgba(201,255,0,0.08);
        }
        
        .conversation-item input[type="checkbox"] {
            width: 18px;
            height: 18px;
            margin-right: 14px;
            margin-top: 2px;
            cursor: pointer;
            accent-color: #C9FF00;
            flex-shrink: 0;
        }
        
        .conversation-item strong {
            font-family: 'DM Sans', sans-serif;
            font-size: 14px;
            color: #e8e8e0;
        }
        
        .conversation-item small {
            display: block;
            margin-top: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #666666;
        }
        
        .conversation-item > div {
            flex: 1;
        }
        
        .btn-primary {
            background: #C9FF00;
            color: #060606;
            border: none;
            padding: 10px 24px;
            border-radius: 30px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 13px;
        }
        
        .btn-primary:hover {
            background: #b3e600;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: transparent;
            border: 1px solid #1e1e1c;
            color: #e8e8e0;
            padding: 10px 24px;
            border-radius: 30px;
            font-family: 'JetBrains Mono', monospace;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 13px;
        }
        
        .btn-secondary:hover {
            border-color: #C9FF00;
            color: #C9FF00;
        }
        
        /* Loading & Error States */
        .loading, .error, .no-data {
            text-align: center;
            padding: 60px 40px;
            background: #0c0c0b;
            border: 1px solid #1e1e1c;
            border-radius: 20px;
            font-family: 'DM Sans', sans-serif;
        }
        
        .loading {
            color: #666666;
        }
        
        .error {
            color: #ff4444;
            border-left: 3px solid #ff4444;
        }
        
        .no-data {
            color: #666666;
            font-style: italic;
        }
        
        /* Toast Notification */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #0c0c0b;
            border: 1px solid #C9FF00;
            border-radius: 12px;
            padding: 16px 24px;
            font-family: 'DM Sans', sans-serif;
            font-size: 14px;
            color: #C9FF00;
            z-index: 1001;
            animation: fadeUp 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 24px 16px;
            }
            
            h1 {
                font-size: 48px;
            }
            
            .subhead {
                font-size: 16px;
            }
            
            .cards-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(3, 1fr);
            }
            
            .header-actions {
                flex-direction: column;
                align-items: stretch;
            }
            
            .button-group {
                justify-content: center;
            }
            
            .tab-btn {
                padding: 8px 12px;
                font-size: 10px;
            }
            
            .card-header h3 {
                font-size: 20px;
            }
            
            .selection-bar {
                flex-direction: column;
                text-align: center;
            }
            
            .selection-actions {
                justify-content: center;
            }
            
            .info-row {
                flex-direction: column;
                gap: 4px;
            }
            
            .info-label {
                min-width: auto;
            }
        }
        
        @media (max-width: 480px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .modal-content {
                width: 95%;
            }
            
            .modal-header h2 {
                font-size: 24px;
            }
            
            .button-group {
                flex-direction: column;
                width: 100%;
            }
            
            .export-btn, .select-export-btn, .refresh-btn {
                width: 100%;
                justify-content: center;
            }
            
            .tabs {
                width: 100%;
            }
            
            .tab-btn {
                flex: 1;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="noise-overlay"></div>
    <div class="orb"></div>
    
    <div class="container">
        <div class="header-actions">
            <div class="title-section">
                <h1>VYNERA</h1>
                <div class="subhead">conversation intelligence · emotional analytics</div>
            </div>
            <div class="button-group">
                <div class="tabs">
                    <button class="tab-btn active" data-tab="conversations">💬 CONVERSATIONS</button>
                    <button class="tab-btn" data-tab="users">👥 USERS</button>
                    <button class="tab-btn" data-tab="feedback">⭐ FEEDBACK</button>
                    <button class="tab-btn" data-tab="goals">🎯 GOALS</button>
                    <button class="tab-btn" data-tab="journals">📓 JOURNALS</button>
                    <button class="tab-btn" data-tab="memories">🧠 MEMORIES</button>
                </div>
                <button class="select-export-btn" onclick="openSelectionModal()">
                    🎯 SELECT & EXPORT
                </button>
                <button class="export-btn" onclick="exportAllConversations()">
                    📄 EXPORT ALL
                </button>
                <button class="refresh-btn" onclick="fetchAllData()">⟳ REFRESH</button>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-grid" id="statsContainer">
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">CONVERSATIONS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">USERS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">FEEDBACK</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">GOALS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">JOURNALS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">MEMORIES</div>
            </div>
        </div>

        <!-- Selection Bar -->
        <div id="selectionBar" class="selection-bar" style="display: none;">
            <div class="selection-info">
                ✓ <span id="selectedCount">0</span> conversation(s) selected
            </div>
            <div class="selection-actions">
                <button class="selection-btn" onclick="selectAll()">Select All</button>
                <button class="selection-btn" onclick="clearSelection()">Clear All</button>
                <button class="selection-btn" onclick="exportSelected()" style="background:#C9FF00; color:#060606;">Export Selected</button>
            </div>
        </div>

        <!-- Conversations Tab -->
        <div id="conversations-tab" class="tab-content active">
            <div id="conversations-container" class="cards-grid">
                <div class="loading">loading conversations...</div>
            </div>
        </div>

        <!-- Users Tab -->
        <div id="users-tab" class="tab-content">
            <div id="users-container" class="cards-grid">
                <div class="loading">loading users...</div>
            </div>
        </div>

        <!-- Feedback Tab -->
        <div id="feedback-tab" class="tab-content">
            <div id="feedback-container" class="cards-grid">
                <div class="loading">loading feedback...</div>
            </div>
        </div>

        <!-- Goals Tab -->
        <div id="goals-tab" class="tab-content">
            <div id="goals-container" class="cards-grid">
                <div class="loading">loading goals...</div>
            </div>
        </div>

        <!-- Journals Tab -->
        <div id="journals-tab" class="tab-content">
            <div id="journals-container" class="cards-grid">
                <div class="loading">loading journals...</div>
            </div>
        </div>

        <!-- Memories Tab -->
        <div id="memories-tab" class="tab-content">
            <div id="memories-container" class="cards-grid">
                <div class="loading">loading memories...</div>
            </div>
        </div>
    </div>

    <!-- Selection Modal -->
    <div id="selectionModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Select Conversations</h2>
                <span class="close-modal" onclick="closeSelectionModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div class="filter-group">
                    <label>FILTER BY USER</label>
                    <select id="userFilter" onchange="filterConversations()">
                        <option value="all">All Users</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>FILTER BY TOPIC</label>
                    <select id="topicFilter" onchange="filterConversations()">
                        <option value="all">All Topics</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>SEARCH</label>
                    <input type="text" id="searchInput" placeholder="Search by title or content..." oninput="filterConversations()">
                </div>
                <div id="conversationList" class="conversation-list">
                    <!-- Dynamic conversation list -->
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="selectAllInModal()">Select All</button>
                <button class="btn-secondary" onclick="clearAllInModal()">Clear All</button>
                <button class="btn-primary" onclick="confirmSelection()">Export Selected (<span id="modalSelectedCount">0</span>)</button>
            </div>
        </div>
    </div>

    <script>
        let usersMap = {};
        let allConversations = [];
        let allUsers = [];
        let allFeedback = [];
        let allGoals = [];
        let allJournals = [];
        let allMemories = [];
        let selectedConversationIds = new Set();
        let filteredConversations = [];
        
        async function fetchAllData() {
            await Promise.all([
                fetchUsers(),
                fetchConversations(),
                fetchFeedback(),
                fetchGoals(),
                fetchJournals(),
                fetchMemories()
            ]);
            updateStats();
        }
        
        async function fetchUsers() {
            try {
                const response = await fetch('/api/users');
                if (!response.ok) throw new Error('Failed to fetch users');
                const users = await response.json();
                allUsers = users;
                usersMap = {};
                users.forEach(user => {
                    usersMap[user._id] = user;
                });
                displayUsers(users);
                updateUserFilter();
            } catch (error) {
                console.error('Error loading users:', error);
                document.getElementById('users-container').innerHTML = `<div class="error">error loading users</div>`;
            }
        }
        
async function fetchConversations() {
    const container = document.getElementById('conversations-container');
    container.innerHTML = '<div class="loading">loading conversations...</div>';
    
    try {
        const response = await fetch('/api/conversations');
        if (!response.ok) throw new Error('Failed to fetch conversations');
        const conversations = await response.json();
        // Sort conversations by created_at in descending order (newest first)
        conversations.sort((a, b) => {
            const dateA = new Date(a.created_at);
            const dateB = new Date(b.created_at);
            return dateB - dateA;
        });
        allConversations = conversations;
        displayConversations(conversations);
        updateTopicFilter();
    } catch (error) {
        container.innerHTML = `<div class="error">error loading conversations</div>`;
    }
}
        
        async function fetchFeedback() {
            try {
                const response = await fetch('/api/feedback');
                if (!response.ok) throw new Error('Failed to fetch feedback');
                const feedback = await response.json();
                allFeedback = feedback;
                displayFeedback(feedback);
            } catch (error) {
                document.getElementById('feedback-container').innerHTML = `<div class="error">error loading feedback</div>`;
            }
        }
        
        async function fetchGoals() {
            try {
                const response = await fetch('/api/goals');
                if (!response.ok) throw new Error('Failed to fetch goals');
                const goals = await response.json();
                allGoals = goals;
                displayGoals(goals);
            } catch (error) {
                document.getElementById('goals-container').innerHTML = `<div class="error">error loading goals</div>`;
            }
        }
        
        async function fetchJournals() {
            try {
                const response = await fetch('/api/journals');
                if (!response.ok) throw new Error('Failed to fetch journals');
                const journals = await response.json();
                allJournals = journals;
                displayJournals(journals);
            } catch (error) {
                document.getElementById('journals-container').innerHTML = `<div class="error">error loading journals</div>`;
            }
        }
        
        async function fetchMemories() {
            try {
                const response = await fetch('/api/memories');
                if (!response.ok) throw new Error('Failed to fetch memories');
                const memories = await response.json();
                allMemories = memories;
                displayMemories(memories);
            } catch (error) {
                document.getElementById('memories-container').innerHTML = `<div class="error">error loading memories</div>`;
            }
        }
        
        function updateStats() {
            document.querySelectorAll('.stat-card')[0].querySelector('.stat-number').textContent = allConversations.length;
            document.querySelectorAll('.stat-card')[1].querySelector('.stat-number').textContent = allUsers.length;
            document.querySelectorAll('.stat-card')[2].querySelector('.stat-number').textContent = allFeedback.length;
            document.querySelectorAll('.stat-card')[3].querySelector('.stat-number').textContent = allGoals.length;
            document.querySelectorAll('.stat-card')[4].querySelector('.stat-number').textContent = allJournals.length;
            document.querySelectorAll('.stat-card')[5].querySelector('.stat-number').textContent = allMemories.length;
        }
        
        function getUserName(userId) {
            if (!userId) return 'Unknown User';
            const user = usersMap[userId];
            if (user) {
                return user.name || user.username || 'Unknown User';
            }
            return 'Unknown User';
        }
        
        function displayConversations(conversations) {
            const container = document.getElementById('conversations-container');
            
            if (!conversations || conversations.length === 0) {
                container.innerHTML = '<div class="no-data">no conversations found</div>';
                return;
            }
            
            container.innerHTML = conversations.map(conv => {
                const safeId = String(conv._id || Math.random()).replace(/[^a-zA-Z0-9]/g, '_');
                const userName = getUserName(conv.user_id);
                const messageCount = conv.messages ? conv.messages.length : 0;
                const isSelected = selectedConversationIds.has(conv._id);
                const title = conv.title || 'Untitled';
                
                return `
                    <div class="card ${isSelected ? 'selected' : ''} fade-up" data-conv-id="${conv._id}">
                        <label class="card-checkbox">
                            <input type="checkbox" onchange="toggleConversationSelection('${conv._id}', this)" ${isSelected ? 'checked' : ''}>
                            <span class="checkmark"></span>
                        </label>
                        <div class="card-header">
                            <h3>${escapeHtml(userName)}</h3>
                            <div class="user-info-badge">
                                <span class="badge">👤 ${escapeHtml(userName)}</span>
                                <span class="badge topic">${escapeHtml(conv.topic || 'neutral')}</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="info-grid">
                                <div class="info-row">
                                    <span class="info-label">CONVERSATION ID</span>
                                    <span class="info-value mono">${escapeHtml(conv._id)}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">USER ID</span>
                                    <span class="info-value mono">${escapeHtml(conv.user_id || 'N/A')}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">MESSAGES</span>
                                    <span class="info-value">${messageCount} messages</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">CREATED</span>
                                    <span class="info-value mono">${formatDate(conv.created_at)}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">UPDATED</span>
                                    <span class="info-value mono">${formatDate(conv.updated_at)}</span>
                                </div>
                            </div>
                            
                            ${conv.mood_scores && conv.mood_scores.length ? `
                            <div class="mood-section">
                                <div class="mood-title">MOOD SCORES · ${conv.mood_scores.length} RECORDS</div>
                                <div class="mood-list">
                                    ${conv.mood_scores.slice(0, 8).map(score => `<span class="mood-score">${escapeHtml(String(score))}</span>`).join('')}
                                    ${conv.mood_scores.length > 8 ? `<span class="mood-score">+${conv.mood_scores.length - 8}</span>` : ''}
                                </div>
                            </div>
                            ` : ''}
                            
                            ${conv.messages && conv.messages.length ? `
                            <div class="messages-section">
                                <div class="messages-title" onclick="toggleMessages(this)">
                                    ⌄ VIEW MESSAGES (${conv.messages.length})
                                </div>
                                <div class="messages-list" id="msg-${safeId}">
                                    ${conv.messages.map((msg, idx) => `
                                        <div class="message ${msg.role === 'user' ? 'user' : 'assistant'}">
                                            <div class="message-header">
                                                <span class="message-role">${msg.role === 'user' ? 'USER' : 'ASSISTANT'}</span>
                                                <span class="message-timestamp">${formatDate(msg.timestamp)}</span>
                                            </div>
                                            <div class="message-content">${escapeHtml(msg.content || '')}</div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            ` : '<div style="margin-top:16px; color:#666666;">no messages in this conversation</div>'}
                        </div>
                    </div>
                `;
            }).join('');
            
            updateSelectionBar();
        }
        
        function displayUsers(users) {
            const container = document.getElementById('users-container');
            
            if (!users || users.length === 0) {
                container.innerHTML = '<div class="no-data">no users found</div>';
                return;
            }
            
            container.innerHTML = users.map(user => {
                return `
                    <div class="card fade-up">
                        <div class="card-header">
                            <h3>${escapeHtml(user.name || user.username || 'Unknown')}</h3>
                            <div class="user-info-badge">
                                <span class="badge">🎭 ${escapeHtml(user.personality || 'unknown')}</span>
                                <span class="badge">@${escapeHtml(user.username || 'no-username')}</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="info-grid">
                                <div class="info-row">
                                    <span class="info-label">FULL NAME</span>
                                    <span class="info-value">${escapeHtml(user.name || '—')}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">EMAIL</span>
                                    <span class="info-value mono">${escapeHtml(user.email || '—')}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">AGE</span>
                                    <span class="info-value">${user.age || '—'}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">USER ID</span>
                                    <span class="info-value mono">${escapeHtml(user._id)}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">CREATED</span>
                                    <span class="info-value mono">${formatDate(user.created_at)}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">UPDATED</span>
                                    <span class="info-value mono">${formatDate(user.updated_at)}</span>
                                </div>
                                ${user.parent_phone ? `
                                <div class="info-row">
                                    <span class="info-label">PARENT PHONE</span>
                                    <span class="info-value mono">${escapeHtml(user.parent_phone)}</span>
                                </div>
                                ` : ''}
                            </div>
                            
                            ${user.questionnaire ? `
                            <div class="messages-section">
                                <div class="messages-title" onclick="toggleMessages(this)">
                                    ⌄ VIEW QUESTIONNAIRE
                                </div>
                                <div class="messages-list">
                                    <pre style="font-family:'JetBrains Mono',monospace; font-size:11px; background:#060606; padding:16px; border-radius:8px; overflow-x:auto;">${escapeHtml(JSON.stringify(user.questionnaire, null, 2))}</pre>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function displayFeedback(feedback) {
            const container = document.getElementById('feedback-container');
            
            if (!feedback || feedback.length === 0) {
                container.innerHTML = '<div class="no-data">no feedback found</div>';
                return;
            }
            
            container.innerHTML = feedback.map(fb => {
                const rating = fb.rating || 0;
                const ratingClass = rating > 0 ? 'positive' : (rating < 0 ? 'negative' : 'neutral');
                const ratingStars = rating > 0 ? '★'.repeat(rating) + '☆'.repeat(5-rating) : (rating < 0 ? '★'.repeat(Math.abs(rating)) + '☆'.repeat(5-Math.abs(rating)) : '☆☆☆☆☆');
                
                return `
                    <div class="card fade-up">
                        <div class="card-header">
                            <h3>User Feedback</h3>
                            <div class="user-info-badge">
                                <span class="badge">👤 ${escapeHtml(getUserName(fb.user_id))}</span>
                                <span class="badge ${ratingClass}">Rating: ${ratingStars}</span>
                                <span class="badge">${fb.processed ? '✅ Processed' : '⏳ Pending'}</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="info-grid">
                                <div class="info-row">
                                    <span class="info-label">FEEDBACK ID</span>
                                    <span class="info-value mono">${escapeHtml(fb._id)}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">CONVERSATION ID</span>
                                    <span class="info-value mono">${escapeHtml(fb.conv_id || 'N/A')}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">USER MESSAGE</span>
                                    <span class="info-value">${escapeHtml(fb.user_message || '—')}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">BOT RESPONSE</span>
                                    <span class="info-value">${escapeHtml(fb.bot_response || '—')}</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">RATING</span>
                                    <span class="info-value rating-stars ${ratingClass}">${ratingStars} (${rating})</span>
                                </div>
                                <div class="info-row">
                                    <span class="info-label">CREATED</span>
                                    <span class="info-value mono">${formatDate(fb.created_at)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function displayGoals(goals) {
            const container = document.getElementById('goals-container');
            
            if (!goals || goals.length === 0) {
                container.innerHTML = '<div class="no-data">no goals found</div>';
                return;
            }
            
            container.innerHTML = goals.map(goal => `
                <div class="card fade-up">
                    <div class="card-header">
                        <h3>${escapeHtml(goal.key || 'Goal')}</h3>
                        <div class="user-info-badge">
                            <span class="badge">👤 ${escapeHtml(getUserName(goal.user_id))}</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="key-value-pair">
                            <div class="key">VALUE</div>
                            <div class="value">${escapeHtml(goal.value || '—')}</div>
                        </div>
                        <div class="info-grid">
                            <div class="info-row">
                                <span class="info-label">GOAL ID</span>
                                <span class="info-value mono">${escapeHtml(goal._id)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">CREATED</span>
                                <span class="info-value mono">${formatDate(goal.created_at)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">UPDATED</span>
                                <span class="info-value mono">${formatDate(goal.updated_at)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function displayJournals(journals) {
            const container = document.getElementById('journals-container');
            
            if (!journals || journals.length === 0) {
                container.innerHTML = '<div class="no-data">no journals found</div>';
                return;
            }
            
            container.innerHTML = journals.map(journal => `
                <div class="card fade-up">
                    <div class="card-header">
                        <h3>Journal Entry</h3>
                        <div class="user-info-badge">
                            <span class="badge">👤 ${escapeHtml(getUserName(journal.user_id))}</span>
                        </div>
                    </div>
                    <div class="card-body">
                        ${journal.key ? `
                        <div class="key-value-pair">
                            <div class="key">${escapeHtml(journal.key)}</div>
                            <div class="value">${escapeHtml(journal.value || '—')}</div>
                        </div>
                        ` : ''}
                        <div class="info-grid">
                            <div class="info-row">
                                <span class="info-label">JOURNAL ID</span>
                                <span class="info-value mono">${escapeHtml(journal._id)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">CREATED</span>
                                <span class="info-value mono">${formatDate(journal.created_at)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">UPDATED</span>
                                <span class="info-value mono">${formatDate(journal.updated_at)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function displayMemories(memories) {
            const container = document.getElementById('memories-container');
            
            if (!memories || memories.length === 0) {
                container.innerHTML = '<div class="no-data">no memories found</div>';
                return;
            }
            
            container.innerHTML = memories.map(memory => `
                <div class="card fade-up">
                    <div class="card-header">
                        <h3>${escapeHtml(memory.key || 'Memory')}</h3>
                        <div class="user-info-badge">
                            <span class="badge">👤 ${escapeHtml(getUserName(memory.user_id))}</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="key-value-pair">
                            <div class="key">VALUE</div>
                            <div class="value">${escapeHtml(memory.value || '—')}</div>
                        </div>
                        <div class="info-grid">
                            <div class="info-row">
                                <span class="info-label">MEMORY ID</span>
                                <span class="info-value mono">${escapeHtml(memory._id)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">CREATED</span>
                                <span class="info-value mono">${formatDate(memory.created_at)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">UPDATED</span>
                                <span class="info-value mono">${formatDate(memory.updated_at)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function toggleConversationSelection(convId, checkbox) {
            if (checkbox.checked) {
                selectedConversationIds.add(convId);
            } else {
                selectedConversationIds.delete(convId);
            }
            
            const card = document.querySelector(`.card[data-conv-id="${convId}"]`);
            if (card) {
                if (checkbox.checked) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            }
            
            updateSelectionBar();
        }
        
        function selectAll() {
            allConversations.forEach(conv => {
                selectedConversationIds.add(conv._id);
                const card = document.querySelector(`.card[data-conv-id="${conv._id}"]`);
                if (card) {
                    card.classList.add('selected');
                    const checkbox = card.querySelector('input[type="checkbox"]');
                    if (checkbox) checkbox.checked = true;
                }
            });
            updateSelectionBar();
            showToast(`Selected ${selectedConversationIds.size} conversations`);
        }
        
        function clearSelection() {
            selectedConversationIds.clear();
            document.querySelectorAll('.card').forEach(card => {
                card.classList.remove('selected');
                const checkbox = card.querySelector('input[type="checkbox"]');
                if (checkbox) checkbox.checked = false;
            });
            updateSelectionBar();
            showToast('Selection cleared');
        }
        
        function updateSelectionBar() {
            const selectionBar = document.getElementById('selectionBar');
            const selectedCount = document.getElementById('selectedCount');
            
            if (selectedConversationIds.size > 0) {
                selectionBar.style.display = 'flex';
                selectedCount.textContent = selectedConversationIds.size;
            } else {
                selectionBar.style.display = 'none';
            }
        }
        
        async function exportSelected() {
            if (selectedConversationIds.size === 0) {
                showToast('No conversations selected');
                return;
            }
            
            const selectedConvs = allConversations.filter(conv => selectedConversationIds.has(conv._id));
            await performExport(selectedConvs);
        }
        
        async function exportAllConversations() {
            await performExport(allConversations);
        }
        
        async function performExport(conversations) {
            const exportBtn = document.querySelector('.export-btn');
            const originalText = exportBtn.innerHTML;
            exportBtn.innerHTML = '⏳ GENERATING...';
            exportBtn.classList.add('loading');
            exportBtn.disabled = true;
            
            try {
                const response = await fetch('/api/export/selected', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        conversation_ids: conversations.map(c => c._id)
                    })
                });
                
                if (!response.ok) throw new Error('Export failed');
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                const timestamp = new Date().toISOString().slice(0,19).replace(/:/g, '-');
                a.download = `vynera_selected_${conversations.length}_conversations_${timestamp}.md`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                showToast(`✅ Exported ${conversations.length} conversation(s)!`);
            } catch (error) {
                console.error('Export error:', error);
                showToast('❌ Export failed. Please try again.');
            } finally {
                exportBtn.innerHTML = originalText;
                exportBtn.classList.remove('loading');
                exportBtn.disabled = false;
            }
        }
        
        function openSelectionModal() {
            const modal = document.getElementById('selectionModal');
            modal.classList.add('active');
            filterConversations();
            updateModalSelectedCount();
        }
        
        function closeSelectionModal() {
            const modal = document.getElementById('selectionModal');
            modal.classList.remove('active');
        }
        
        function updateUserFilter() {
            const userFilter = document.getElementById('userFilter');
            const userIds = [...new Set(allConversations.map(c => c.user_id).filter(id => id))];
            userFilter.innerHTML = '<option value="all">All Users</option>';
            userIds.forEach(userId => {
                const user = usersMap[userId];
                const userName = user ? (user.name || user.username) : 'Unknown User';
                userFilter.innerHTML += `<option value="${userId}">${escapeHtml(userName)}</option>`;
            });
        }
        
        function updateTopicFilter() {
            const topicFilter = document.getElementById('topicFilter');
            const topics = [...new Set(allConversations.map(c => c.topic).filter(t => t))];
            topicFilter.innerHTML = '<option value="all">All Topics</option>';
            topics.forEach(topic => {
                topicFilter.innerHTML += `<option value="${topic}">${escapeHtml(topic)}</option>`;
            });
        }
        
        function filterConversations() {
            const userFilter = document.getElementById('userFilter').value;
            const topicFilter = document.getElementById('topicFilter').value;
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            
            filteredConversations = allConversations.filter(conv => {
                if (userFilter !== 'all' && conv.user_id !== userFilter) return false;
                if (topicFilter !== 'all' && conv.topic !== topicFilter) return false;
                if (searchTerm) {
                    const titleMatch = conv.title?.toLowerCase().includes(searchTerm);
                    const contentMatch = conv.messages?.some(m => m.content?.toLowerCase().includes(searchTerm));
                    if (!titleMatch && !contentMatch) return false;
                }
                return true;
            });
            
            updateConversationList();
        }
        
        function updateConversationList() {
    const container = document.getElementById('conversationList');
    let conversationsToShow = filteredConversations.length ? filteredConversations : allConversations;
    
    // Sort conversations by created_at in descending order (newest first)
    conversationsToShow = [...conversationsToShow].sort((a, b) => {
        const dateA = new Date(a.created_at);
        const dateB = new Date(b.created_at);
        return dateB - dateA;
    });
    
    if (conversationsToShow.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding:40px; color:#666666;">No conversations match your filters</div>';
        return;
    }
    
    container.innerHTML = conversationsToShow.map(conv => {
        const userName = getUserName(conv.user_id);
        const isSelected = selectedConversationIds.has(conv._id);
        return `
            <div class="conversation-item ${isSelected ? 'selected' : ''}" onclick="toggleConversationInModal('${conv._id}', event)">
                <input type="checkbox" ${isSelected ? 'checked' : ''} onclick="event.stopPropagation(); toggleConversationInModal('${conv._id}', event)">
                <div>
                    <strong>${escapeHtml(conv.title || 'Untitled')}</strong>
                    <small>User: ${escapeHtml(userName)} | Topic: ${escapeHtml(conv.topic || 'neutral')} | Messages: ${conv.messages?.length || 0} | Created: ${formatDate(conv.created_at)}</small>
                </div>
            </div>
        `;
    }).join('');
    
    updateModalSelectedCount();
}
        
        function toggleConversationInModal(convId, event) {
            if (selectedConversationIds.has(convId)) {
                selectedConversationIds.delete(convId);
            } else {
                selectedConversationIds.add(convId);
            }
            updateConversationList();
            updateModalSelectedCount();
            displayConversations(allConversations);
        }
        
        function selectAllInModal() {
            const conversationsToSelect = filteredConversations.length ? filteredConversations : allConversations;
            conversationsToSelect.forEach(conv => {
                selectedConversationIds.add(conv._id);
            });
            updateConversationList();
            updateModalSelectedCount();
            displayConversations(allConversations);
            showToast(`Selected ${selectedConversationIds.size} conversations`);
        }
        
        function clearAllInModal() {
            const conversationsToClear = filteredConversations.length ? filteredConversations : allConversations;
            conversationsToClear.forEach(conv => {
                selectedConversationIds.delete(conv._id);
            });
            updateConversationList();
            updateModalSelectedCount();
            displayConversations(allConversations);
            showToast('Selection cleared');
        }
        
        function confirmSelection() {
            closeSelectionModal();
            updateSelectionBar();
            displayConversations(allConversations);
            showToast(`${selectedConversationIds.size} conversation(s) selected`);
        }
        
        function updateModalSelectedCount() {
            const countSpan = document.getElementById('modalSelectedCount');
            if (countSpan) {
                countSpan.textContent = selectedConversationIds.size;
            }
        }
        
        function toggleMessages(element) {
            const messagesList = element.nextElementSibling;
            if (messagesList) {
                messagesList.classList.toggle('open');
                if (messagesList.classList.contains('open')) {
                    element.innerHTML = element.innerHTML.replace('VIEW', 'HIDE');
                } else {
                    element.innerHTML = element.innerHTML.replace('HIDE', 'VIEW');
                }
            }
        }
        
        function formatDate(dateString) {
            if (!dateString) return '—';
            try {
                const date = new Date(dateString);
                return date.toLocaleString('en-US', { 
                    year: 'numeric', 
                    month: 'short', 
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch(e) {
                return String(dateString);
            }
        }
        
        function escapeHtml(str) {
            if (!str) return '';
            return String(str)
                .replace(/[&<>]/g, function(m) {
                    if (m === '&') return '&amp;';
                    if (m === '<') return '&lt;';
                    if (m === '>') return '&gt;';
                    return m;
                });
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
        
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tabName = btn.dataset.tab;
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
                document.getElementById(`${tabName}-tab`).classList.add('active');
            });
        });
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('selectionModal');
            if (event.target === modal) {
                closeSelectionModal();
            }
        }
        
        // Initial load
        fetchAllData();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/export/selected', methods=['POST'])
def export_selected():
    """Export selected conversations to a single Markdown file"""
    try:
        data = request.get_json()
        conversation_ids = data.get('conversation_ids', [])
        
        if not conversation_ids:
            return jsonify({'error': 'No conversations selected'}), 400
        
        # Fetch selected conversations
        selected_conversations = []
        for conv_id in conversation_ids:
            try:
                conv = conversations_collection.find_one({'_id': ObjectId(conv_id)})
                if conv:
                    selected_conversations.append(convert_doc(conv))
            except:
                continue
        
        # Fetch all users for mapping
        users = list(users_collection.find())
        users_map = {}
        for user in users:
            cleaned_user = convert_doc(user)
            users_map[str(cleaned_user.get('_id', ''))] = cleaned_user
        
        # Generate markdown file
        md_content = generate_selected_md_file(selected_conversations, users_map)
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"vynera_selected_{len(selected_conversations)}_conversations_{timestamp}.md"
        
        # Convert to bytes for sending
        md_bytes = md_content.encode('utf-8')
        
        return send_file(
            BytesIO(md_bytes),
            as_attachment=True,
            download_name=filename,
            mimetype='text/markdown'
        )
        
    except Exception as e:
        print(f"Export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations')
def get_conversations():
    try:
        # Sort by created_at in descending order (newest first)
        conversations = list(conversations_collection.find().sort('created_at', -1))
        cleaned_conversations = []
        
        for conv in conversations:
            try:
                cleaned_conv = convert_doc(conv)
                cleaned_conversations.append(cleaned_conv)
            except Exception as e:
                print(f"Error cleaning conversation: {str(e)}")
                fallback = {
                    '_id': str(conv.get('_id', 'unknown')),
                    'title': 'Data Error',
                    'topic': 'error',
                    'messages': [],
                    'mood_scores': [],
                    'created_at': None,
                    'updated_at': None,
                    'user_id': 'unknown'
                }
                cleaned_conversations.append(fallback)
        
        return app.response_class(
            response=json.dumps(cleaned_conversations, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in get_conversations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users')
def get_users():
    try:
        users = list(users_collection.find())
        cleaned_users = []
        
        for user in users:
            try:
                cleaned_user = convert_doc(user)
                cleaned_users.append(cleaned_user)
            except Exception as e:
                print(f"Error cleaning user: {str(e)}")
                fallback = {
                    '_id': str(user.get('_id', 'unknown')),
                    'name': 'Data Error',
                    'username': 'error',
                    'email': 'error',
                    'personality': 'unknown',
                    'created_at': None,
                    'updated_at': None
                }
                cleaned_users.append(fallback)
        
        return app.response_class(
            response=json.dumps(cleaned_users, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in get_users: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback')
def get_feedback():
    try:
        feedback = list(feedback_collection.find())
        cleaned_feedback = [convert_doc(fb) for fb in feedback]
        return app.response_class(
            response=json.dumps(cleaned_feedback, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in get_feedback: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/goals')
def get_goals():
    try:
        goals = list(goals_collection.find())
        cleaned_goals = [convert_doc(goal) for goal in goals]
        return app.response_class(
            response=json.dumps(cleaned_goals, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in get_goals: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/journals')
def get_journals():
    try:
        journals = list(journals_collection.find())
        cleaned_journals = [convert_doc(journal) for journal in journals]
        return app.response_class(
            response=json.dumps(cleaned_journals, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in get_journals: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/memories')
def get_memories():
    try:
        memories = list(memories_collection.find())
        cleaned_memories = [convert_doc(memory) for memory in memories]
        return app.response_class(
            response=json.dumps(cleaned_memories, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error in get_memories: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🎭 VYNERA Dashboard Server Starting...")
    print(f"📁 Database: vynera")
    print(f"📊 Collections: conversations, users, feedback, goal, journals, memories")
    print("🌐 Open http://localhost:5000 in your browser")
    print("✨ Features:")
    print("   • Complete dashboard with 6 collections")
    print("   • Real-time statistics overview")
    print("   • Custom themed checkboxes matching VYNERA design")
    print("   • Select individual conversations using checkboxes")
    print("   • Use SELECT & EXPORT for filtered selection")
    print("   • Export ALL conversations with one click")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)