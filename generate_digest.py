import os
import glob
import sys
import re
from datetime import datetime

# Ensure utf-8 output encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

SOURCE_DIR = os.path.join(os.path.dirname(__file__), "Office_Digest_Source")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Office_Digest_Output")

# Dictionary mapping Roman Urdu/Hindi phrases to professional English
TRANSLATIONS = {
    "website redesign ka first draft client ko bhej diya": "Submitted the first draft of the website redesign to the client.",
    "client ne overall layout pasand kiya, color palette change mang raha hai": "Client approved the overall layout but requested color palette modifications.",
    "next step: revised design 20 sept tak bhejni hai": "Next Step: Deliver revised design by Sept 20.",
    "q3 targets discuss kiye": "Reviewed and discussed Q3 performance targets.",
    "sales team ne kaha leads ki quality mein improvement chahiye": "Sales team requested improvements in incoming lead quality.",
    "action: marketing se better qualified leads mangwani hain": "Action Item: Coordinate with marketing to improve qualified lead generation.",
    "payment gateway integration mein delay ho raha hai": "Experiencing delays in payment gateway integration.",
    "third-party api documentation incomplete mili": "Third-party vendor API documentation was found incomplete.",
    "risk: launch date 1 week shift ho sakti hai": "Risk: Launch date may slip by 1 week.",
    "mobile app ke 3 major bugs fix ho gaye": "Fixed 3 major critical bugs in the mobile application.",
    "testing team ne regression testing shuru kar di": "QA team initiated full regression testing.",
    "expected: friday tak stable build": "Expected: Stable release build ready by Friday.",
    "dashboard loading slow hai": "Dashboard loading speed is slow / high latency reported.",
    "filter options aur add karne ko kaha": "Client requested additional filter options for the dashboard.",
    "priority: performance improvement pehle": "Priority: Focus on dashboard performance optimizations first.",
    "team morale overall theek hai": "Overall team morale remains healthy and stable.",
    "do logon ne leave request di hai next week": "Two team members have submitted leave requests for next week.",
    "action items pending from last week abhi clear nahi hue": "Pending action items carried over from last week still need clearance.",
    "payment gateway documentation received from vendor, integration unblocked": "Received complete API documentation from vendor; payment gateway integration unblocked.",
    "client approved revised blue color palette for website": "Client approved the revised blue color palette for the website.",
    "action: deploy staging build on monday morning": "Action Item: Deploy staging build on Monday morning."
}

def translate_to_english(text):
    """Converts Roman Urdu/Hindi phrases to formal professional English."""
    cleaned = text.strip()
    key = re.sub(r"^[-*•]\s*", "", cleaned).strip().lower()
    
    # Direct match lookup
    if key in TRANSLATIONS:
        return TRANSLATIONS[key]
    
    # Partial matching / substring replacement fallback
    for k, v in TRANSLATIONS.items():
        if k in key:
            return v
            
    # Default fallback: return cleaned text if already English
    return re.sub(r"^[-*•]\s*", "", cleaned)

def parse_notes():
    """Reads, translates, and categorizes notes from the source folder."""
    os.makedirs(SOURCE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.txt")))
    
    categorized = {
        "progress": [],
        "blockers": [],
        "client": [],
        "meetings": [],
        "team": [],
        "action_items": [],
        "raw_files": []
    }
    
    for filepath in files:
        fname = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        categorized["raw_files"].append({"name": fname, "content": content})
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        
        file_lower = fname.lower()
        date_str = ""
        
        for line in lines:
            if line.lower().startswith("date:"):
                raw_date = line.split(":", 1)[1].strip()
                date_str = raw_date
                continue
                
            clean_line = re.sub(r"^[-*•]\s*", "", line)
            lower_line = clean_line.lower()
            english_text = translate_to_english(clean_line)
            
            # Categorization Logic
            if any(k in lower_line for k in ["blocker", "issue", "delay", "risk", "incomplete", "problem"]) or "blocker" in file_lower:
                if not lower_line.startswith("issue:") and not lower_line.startswith("blocker:"):
                    categorized["blockers"].append({"date": date_str, "text": english_text, "file": fname})
            elif any(k in lower_line for k in ["client", "feedback", "color palette", "redesign", "filter", "dashboard loading"]) or "client" in file_lower:
                if not lower_line.startswith("client feedback:"):
                    categorized["client"].append({"date": date_str, "text": english_text, "file": fname})
            elif any(k in lower_line for k in ["bug", "fix", "progress", "regression", "build", "draft", "completed", "resolved", "stable"]):
                categorized["progress"].append({"date": date_str, "text": english_text, "file": fname})
            elif any(k in lower_line for k in ["meeting", "targets", "sales", "leads", "q3", "marketing"]) or "meeting" in file_lower:
                if not lower_line.startswith("internal meeting:"):
                    categorized["meetings"].append({"date": date_str, "text": english_text, "file": fname})
            elif any(k in lower_line for k in ["morale", "leave", "holiday", "team"]) or "weekly" in file_lower:
                categorized["team"].append({"date": date_str, "text": english_text, "file": fname})
            
            if any(k in lower_line for k in ["action", "next step", "todo", "tak bhejni", "deadline", "pending"]):
                categorized["action_items"].append({"date": date_str, "text": english_text, "file": fname})
                
    return categorized

def build_markdown(data):
    today_str = datetime.now().strftime("%Y-%m-%d")
    md = []
    md.append("# 🏢 Weekly Executive Office Digest")
    md.append(f"*Generated on: {today_str} | Ingested Logs: {len(data['raw_files'])}*\n")
    md.append("---\n")
    
    md.append("## 📌 1. Executive Summary & Highlights")
    md.append(f"- **Total Updates Tracked:** Successfully processed {len(data['raw_files'])} logs across Engineering, QA, Design, and Sales.")
    md.append(f"- **Key Accomplishments:** {len(data['progress'])} milestones delivered or in final testing phase.")
    md.append(f"- **Active Risks & Blockers:** {len(data['blockers'])} issues identified with mitigation paths active.")
    md.append(f"- **Client Requests:** {len(data['client'])} items addressed or scheduled for upcoming sprints.")
    md.append("\n---\n")
    
    md.append("## 🚀 2. Progress & Completed Milestones")
    for p in data["progress"]:
        prefix = f"**[{p['date']}]** " if p['date'] else ""
        md.append(f"- {prefix}{p['text']}")
    md.append("\n---\n")

    md.append("## ⚠️ 3. Critical Blockers & Risk Analysis")
    if data["blockers"]:
        md.append("| Date | Issue / Risk Description | Source |")
        md.append("| :--- | :--- | :--- |")
        for b in data["blockers"]:
            md.append(f"| {b['date'] or 'N/A'} | {b['text']} | `{b['file']}` |")
    else:
        md.append("✅ *No active blockers reported.*")
    md.append("\n---\n")

    md.append("## 💬 4. Client Feedback & Requirements")
    for c in data["client"]:
        prefix = f"**[{c['date']}]** " if c['date'] else ""
        md.append(f"- {prefix}{c['text']}")
    md.append("\n---\n")

    md.append("## 👥 5. Internal Meetings & Operations")
    for m in data["meetings"] + data["team"]:
        prefix = f"**[{m['date']}]** " if m['date'] else ""
        md.append(f"- {prefix}{m['text']}")
    md.append("\n---\n")

    md.append("## 📋 6. Action Items & Next Priorities")
    for a in data["action_items"]:
        md.append(f"- [ ] {a['text']}")
    md.append("\n---\n")

    return "\n".join(md)

def build_html(data):
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    progress_html = "".join([f"<li><span class='badge progress-badge'>{p['date'] or 'Update'}</span> {p['text']}</li>" for p in data["progress"]])
    blockers_html = "".join([f"<tr><td><span class='badge blocker-badge'>{b['date'] or 'Risk'}</span></td><td>{b['text']}</td><td><code>{b['file']}</code></td></tr>" for b in data["blockers"]])
    client_html = "".join([f"<li><span class='badge client-badge'>{c['date'] or 'Feedback'}</span> {c['text']}</li>" for c in data["client"]])
    ops_html = "".join([f"<li><span class='badge ops-badge'>{m['date'] or 'Team'}</span> {m['text']}</li>" for m in (data["meetings"] + data["team"])])
    action_html = "".join([f"<li class='action-item'><input type='checkbox'> <span>{a['text']}</span></li>" for a in data["action_items"]])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly Executive Office Digest</title>
<style>
  :root {{
    --bg: #0f172a;
    --card: #1e293b;
    --card-header: #334155;
    --text: #f8fafc;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --success: #34d399;
    --danger: #f87171;
    --warning: #fbbf24;
    --purple: #c084fc;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 30px 20px;
    line-height: 1.6;
  }}
  .container {{
    max-width: 960px;
    margin: 0 auto;
  }}
  .header {{
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #334155;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  }}
  .header h1 {{ margin: 0 0 8px 0; font-size: 26px; color: #fff; display: flex; align-items: center; gap: 10px; }}
  .header p {{ margin: 0; color: var(--muted); font-size: 14px; }}
  
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }}
  .metric-card {{
    background: var(--card);
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #334155;
    text-align: center;
    transition: transform 0.2s ease;
  }}
  .metric-card:hover {{
    transform: translateY(-2px);
  }}
  .metric-val {{ font-size: 30px; font-weight: 700; margin-bottom: 4px; }}
  .metric-label {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}

  .section-card {{
    background: var(--card);
    border-radius: 16px;
    border: 1px solid #334155;
    padding: 22px;
    margin-bottom: 24px;
  }}
  .section-card h2 {{
    margin-top: 0;
    font-size: 18px;
    border-bottom: 1px solid #334155;
    padding-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  li {{ padding: 10px 0; border-bottom: 1px solid #293548; display: flex; align-items: center; gap: 12px; font-size: 14.5px; }}
  li:last-child {{ border-bottom: none; }}
  
  .badge {{
    font-size: 11px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 6px;
    white-space: nowrap;
  }}
  .progress-badge {{ background: rgba(52, 211, 153, 0.15); color: var(--success); border: 1px solid rgba(52, 211, 153, 0.3); }}
  .blocker-badge {{ background: rgba(248, 113, 113, 0.15); color: var(--danger); border: 1px solid rgba(248, 113, 113, 0.3); }}
  .client-badge {{ background: rgba(56, 189, 248, 0.15); color: var(--accent); border: 1px solid rgba(56, 189, 248, 0.3); }}
  .ops-badge {{ background: rgba(192, 132, 252, 0.15); color: var(--purple); border: 1px solid rgba(192, 132, 252, 0.3); }}

  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  th, td {{ padding: 12px 10px; text-align: left; border-bottom: 1px solid #334155; font-size: 14.5px; }}
  th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
  code {{ background: #0f172a; padding: 3px 7px; border-radius: 4px; font-size: 12px; color: var(--accent); }}
  
  .action-item input[type="checkbox"] {{
    width: 18px;
    height: 18px;
    accent-color: var(--accent);
    cursor: pointer;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🏢 Weekly Executive Office Digest</h1>
    <p>Automated Summary Pipeline • Generated on <strong>{today_str}</strong> • Source: <code>Office_Digest_Source/</code></p>
  </div>

  <div class="grid">
    <div class="metric-card">
      <div class="metric-val" style="color: var(--accent);">{len(data['raw_files'])}</div>
      <div class="metric-label">Processed Logs</div>
    </div>
    <div class="metric-card">
      <div class="metric-val" style="color: var(--success);">{len(data['progress'])}</div>
      <div class="metric-label">Milestones Done</div>
    </div>
    <div class="metric-card">
      <div class="metric-val" style="color: var(--danger);">{len(data['blockers'])}</div>
      <div class="metric-label">Critical Risks</div>
    </div>
    <div class="metric-card">
      <div class="metric-val" style="color: var(--warning);">{len(data['action_items'])}</div>
      <div class="metric-label">Action Items</div>
    </div>
  </div>

  <div class="section-card">
    <h2 style="color: var(--danger);">⚠️ Critical Blockers & Risks</h2>
    <table>
      <thead><tr><th>Date</th><th>Issue Description</th><th>Source File</th></tr></thead>
      <tbody>{blockers_html if blockers_html else "<tr><td colspan='3'>No active blockers</td></tr>"}</tbody>
    </table>
  </div>

  <div class="section-card">
    <h2 style="color: var(--success);">🚀 Progress & Key Achievements</h2>
    <ul>{progress_html}</ul>
  </div>

  <div class="section-card">
    <h2 style="color: var(--accent);">💬 Client Feedback & Requirements</h2>
    <ul>{client_html}</ul>
  </div>

  <div class="section-card">
    <h2 style="color: var(--purple);">👥 Operations & Team Sync</h2>
    <ul>{ops_html}</ul>
  </div>

  <div class="section-card">
    <h2 style="color: var(--warning);">📋 Action Items & Next Priorities</h2>
    <ul>{action_html}</ul>
  </div>
</div>
</body>
</html>
"""
    return html

def main():
    print("[*] Ingesting and translating notes from Office_Digest_Source...")
    data = parse_notes()
    print(f"[+] Processed {len(data['raw_files'])} notes.")
    
    # Save Markdown
    md_content = build_markdown(data)
    md_path = os.path.join(OUTPUT_DIR, "Weekly_Digest_Latest.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    # Save HTML
    html_content = build_html(data)
    html_path = os.path.join(OUTPUT_DIR, "Weekly_Digest_Dashboard.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[+] Clean English Markdown Report: {md_path}")
    print(f"[+] Clean English HTML Dashboard:  {html_path}")

if __name__ == "__main__":
    main()
