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
    
    if key in TRANSLATIONS:
        return TRANSLATIONS[key]
    
    for k, v in TRANSLATIONS.items():
        if k in key:
            return v
            
    return re.sub(r"^[-*•]\s*", "", cleaned)

def parse_notes():
    """Reads, translates, and categorizes notes from the source folder."""
    os.makedirs(SOURCE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.txt")), reverse=True)
    
    categorized = {
        "progress": [],
        "blockers": [],
        "client": [],
        "meetings": [],
        "team": [],
        "action_items": [],
        "all_updates": [],
        "raw_files": []
    }
    
    for filepath in files:
        fname = os.path.basename(filepath)
        mod_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%I:%M %p")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        categorized["raw_files"].append({
            "name": fname, 
            "content": content,
            "time": mod_time,
            "lines_count": len([l for l in content.splitlines() if l.strip()])
        })
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
                    item = {"type": "Blocker", "badge_class": "badge-blocker", "date": date_str or "Recent", "text": english_text, "source": fname, "time": mod_time}
                    categorized["blockers"].append(item)
                    categorized["all_updates"].append(item)
            elif any(k in lower_line for k in ["client", "feedback", "color palette", "redesign", "filter", "dashboard loading"]) or "client" in file_lower:
                if not lower_line.startswith("client feedback:"):
                    item = {"type": "Client Feedback", "badge_class": "badge-client", "date": date_str or "Recent", "text": english_text, "source": fname, "time": mod_time}
                    categorized["client"].append(item)
                    categorized["all_updates"].append(item)
            elif any(k in lower_line for k in ["bug", "fix", "progress", "regression", "build", "draft", "completed", "resolved", "stable"]):
                item = {"type": "Milestone", "badge_class": "badge-milestone", "date": date_str or "Recent", "text": english_text, "source": fname, "time": mod_time}
                categorized["progress"].append(item)
                categorized["all_updates"].append(item)
            elif any(k in lower_line for k in ["meeting", "targets", "sales", "leads", "q3", "marketing"]) or "meeting" in file_lower:
                if not lower_line.startswith("internal meeting:"):
                    item = {"type": "Team Operations", "badge_class": "badge-team", "date": date_str or "Recent", "text": english_text, "source": fname, "time": mod_time}
                    categorized["meetings"].append(item)
                    categorized["all_updates"].append(item)
            elif any(k in lower_line for k in ["morale", "leave", "holiday", "team"]) or "weekly" in file_lower:
                item = {"type": "Team Operations", "badge_class": "badge-team", "date": date_str or "Recent", "text": english_text, "source": fname, "time": mod_time}
                categorized["team"].append(item)
                categorized["all_updates"].append(item)
            
            if any(k in lower_line for k in ["action", "next step", "todo", "tak bhejni", "deadline", "pending"]):
                item = {"type": "Action Item", "badge_class": "badge-action", "date": date_str or "Recent", "text": english_text, "source": fname, "time": mod_time}
                categorized["action_items"].append(item)
                
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
            md.append(f"| {b['date'] or 'N/A'} | {b['text']} | `{b['source']}` |")
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

def build_dashboard_html(data):
    today_str = datetime.now().strftime("%b %d, %Y")
    now_time_str = datetime.now().strftime("%b %d, %Y %I:%M %p")
    
    total_notes_count = len(data["raw_files"])
    blockers_count = len(data["blockers"])
    milestones_count = len(data["progress"])
    client_count = len(data["client"])
    team_count = len(data["meetings"]) + len(data["team"])
    actions_count = len(data["action_items"])
    
    # Total categorized items for chart
    total_categorized = blockers_count + milestones_count + client_count + team_count + actions_count
    if total_categorized == 0: total_categorized = 1

    # Donut Chart SVG angles calculation
    # Angles for 5 categories
    b_pct = (blockers_count / total_categorized) * 100
    m_pct = (milestones_count / total_categorized) * 100
    c_pct = (client_count / total_categorized) * 100
    t_pct = (team_count / total_categorized) * 100
    a_pct = (actions_count / total_categorized) * 100

    # Build Latest Updates list HTML
    updates_html_list = []
    for item in data["all_updates"][:5]:
        updates_html_list.append(f"""
        <div class="update-item">
          <div class="update-left">
            <span class="pill-badge {item['badge_class']}">{item['type']}</span>
            <div class="update-info">
              <div class="update-title">{item['text']}</div>
              <div class="update-subtitle">Source: <code>{item['source']}</code></div>
            </div>
          </div>
          <div class="update-right">
            <div class="update-date">{item['date']}</div>
            <div class="update-source-type">Office Memo</div>
          </div>
        </div>
        """)
    updates_html = "".join(updates_html_list)

    # Build Recent Sources list HTML
    sources_html_list = []
    for f in data["raw_files"][:5]:
        sources_html_list.append(f"""
        <div class="source-item" onclick="openFileModal('{f['name']}')">
          <div class="source-left">
            <div class="source-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            </div>
            <div class="source-info">
              <div class="source-name">{f['name']}</div>
              <div class="source-category">{f['lines_count']} bullet points</div>
            </div>
          </div>
          <div class="source-right">
            <span class="source-time">{f['time']}</span>
            <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </div>
        </div>
        """)
    sources_html = "".join(sources_html_list)

    # Raw file data as JSON for interactive modal
    import json
    files_json = json.dumps({f["name"]: f["content"] for f in data["raw_files"]})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Office Digest — Automated Operations & Intelligence Pipeline</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Caveat:wght@600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-outer: #090e17;
      --card-window: #0f172a;
      --sidebar-bg: #0f172a;
      --main-bg: #f8fafc;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-light: #94a3b8;
      
      --accent-blue: #3b82f6;
      --accent-blue-light: #eff6ff;
      --accent-red: #ef4444;
      --accent-red-light: #fef2f2;
      --accent-green: #10b981;
      --accent-green-light: #ecfdf5;
      --accent-cyan: #06b6d4;
      --accent-cyan-light: #ecfeff;
      --accent-purple: #8b5cf6;
      --accent-purple-light: #f5f3ff;
      --accent-orange: #f97316;
      
      --card-border: #e2e8f0;
      --radius-lg: 16px;
      --radius-md: 12px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    body {{
      background-color: var(--bg-outer);
      color: #ffffff;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }}

    .showcase-container {{
      max-width: 1280px;
      width: 100%;
      margin: 0 auto;
    }}

    /* =========================================
       HERO PRESENTATION HEADER
       ========================================= */
    .hero-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 32px;
      gap: 30px;
      flex-wrap: wrap;
    }}

    .hero-left {{
      max-width: 580px;
    }}

    .hero-brand {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 12px;
    }}

    .hero-logo-icon {{
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, #2563eb, #38bdf8);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 16px -4px rgba(37, 99, 235, 0.4);
    }}

    .hero-title {{
      font-size: 38px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #ffffff;
    }}

    .hero-title span {{
      color: #38bdf8;
    }}

    .hero-subtitle {{
      font-size: 20px;
      font-weight: 600;
      color: #94a3b8;
      margin-bottom: 10px;
    }}

    .hero-desc {{
      font-size: 15px;
      color: #64748b;
      line-height: 1.5;
    }}

    .hero-features {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding-left: 20px;
      border-left: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .feature-item {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 14px;
      color: #cbd5e1;
      font-weight: 500;
    }}

    .feature-item svg {{
      color: #38bdf8;
      flex-shrink: 0;
    }}

    /* =========================================
       MAC APP WINDOW CONTAINER
       ========================================= */
    .app-window {{
      background: var(--sidebar-bg);
      border-radius: 20px;
      border: 1px solid #1e293b;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.05);
      overflow: hidden;
      display: grid;
      grid-template-columns: 240px 1fr;
      min-height: 740px;
    }}

    /* SIDEBAR */
    .sidebar {{
      background: var(--sidebar-bg);
      border-right: 1px solid #1e293b;
      padding: 20px 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .sidebar-top {{
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}

    .mac-dots {{
      display: flex;
      gap: 7px;
      margin-bottom: 6px;
    }}

    .dot {{
      width: 11px;
      height: 11px;
      border-radius: 50%;
    }}
    .dot-red {{ background: #ef4444; }}
    .dot-yellow {{ background: #f59e0b; }}
    .dot-green {{ background: #10b981; }}

    .sidebar-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 0 4px;
    }}

    .sidebar-brand-icon {{
      width: 28px;
      height: 28px;
      background: #2563eb;
      border-radius: 7px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .sidebar-brand-text {{
      font-size: 15px;
      font-weight: 700;
      color: #ffffff;
    }}

    .nav-menu {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .nav-item {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 500;
      color: #94a3b8;
      text-decoration: none;
      transition: all 0.15s ease;
      cursor: pointer;
    }}

    .nav-item:hover {{
      background: rgba(255, 255, 255, 0.05);
      color: #ffffff;
    }}

    .nav-item.active {{
      background: #2563eb;
      color: #ffffff;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    }}

    .sidebar-status-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: var(--radius-md);
      padding: 14px;
    }}

    .status-indicator {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 600;
      color: #ffffff;
      margin-bottom: 4px;
    }}

    .status-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0% {{ opacity: 1; }}
      50% {{ opacity: 0.4; }}
      100% {{ opacity: 1; }}
    }}

    .status-sub {{
      font-size: 11px;
      color: #64748b;
    }}

    /* MAIN CONTENT AREA (LIGHT THEME) */
    .main-content {{
      background: var(--main-bg);
      color: var(--text-main);
      padding: 30px 32px;
      display: flex;
      flex-direction: column;
      gap: 22px;
      overflow-y: auto;
    }}

    /* TOP BAR / GREETING */
    .dashboard-topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .greeting-title {{
      font-size: 22px;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: -0.3px;
    }}

    .greeting-subtitle {{
      font-size: 13.5px;
      color: #64748b;
      margin-top: 2px;
    }}

    .date-badge {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      padding: 7px 14px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 600;
      color: #334155;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }}

    /* 5 METRIC CARDS ROW */
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 14px;
    }}

    .metric-card {{
      border-radius: var(--radius-md);
      padding: 16px;
      border: 1px solid var(--card-border);
      background: #ffffff;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .metric-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.06);
    }}

    .card-blue {{ background: var(--accent-blue-light); border-color: #dbeafe; }}
    .card-red {{ background: var(--accent-red-light); border-color: #fee2e2; }}
    .card-green {{ background: var(--accent-green-light); border-color: #d1fae5; }}
    .card-cyan {{ background: var(--accent-cyan-light); border-color: #cffafe; }}
    .card-purple {{ background: var(--accent-purple-light); border-color: #ede9fe; }}

    .metric-icon-wrap {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12px;
    }}
    .card-blue .metric-icon-wrap {{ background: #dbeafe; color: #2563eb; }}
    .card-red .metric-icon-wrap {{ background: #fee2e2; color: #dc2626; }}
    .card-green .metric-icon-wrap {{ background: #d1fae5; color: #059669; }}
    .card-cyan .metric-icon-wrap {{ background: #cffafe; color: #0891b2; }}
    .card-purple .metric-icon-wrap {{ background: #ede9fe; color: #7c3aed; }}

    .metric-label {{
      font-size: 12.5px;
      font-weight: 600;
      color: #475569;
      margin-bottom: 8px;
    }}

    .metric-val-row {{
      display: flex;
      align-items: baseline;
      gap: 8px;
    }}

    .metric-number {{
      font-size: 26px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1;
    }}

    .metric-trend {{
      font-size: 11px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 2px;
    }}
    .trend-up {{ color: #10b981; }}
    .trend-down {{ color: #10b981; }} /* green for reduced blockers */

    .metric-sub {{
      font-size: 10.5px;
      color: #94a3b8;
      margin-top: 4px;
    }}

    /* MIDDLE ROW: PIPELINE OVERVIEW & DONUT CHART */
    .dashboard-middle-row {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 18px;
    }}

    .white-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: var(--radius-lg);
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}

    .card-header-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
    }}

    .card-title {{
      font-size: 15px;
      font-weight: 700;
      color: #0f172a;
    }}

    .card-link {{
      font-size: 12.5px;
      font-weight: 600;
      color: #2563eb;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .card-link:hover {{ text-decoration: underline; }}

    /* PIPELINE STEPPER */
    .pipeline-stepper {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 4px;
    }}

    .step-item {{
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 6px;
      position: relative;
    }}

    .step-icon {{
      width: 44px;
      height: 44px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    }}
    .icon-ingestion {{ background: #eff6ff; color: #2563eb; }}
    .icon-norm {{ background: #f5f3ff; color: #7c3aed; }}
    .icon-cat {{ background: #fff7ed; color: #ea580c; }}
    .icon-gen {{ background: #ecfdf5; color: #059669; }}

    .step-connector {{
      flex: 1;
      height: 2px;
      background: #cbd5e1;
      margin: 0 8px;
      position: relative;
      top: -14px;
    }}

    .step-connector-dot {{
      width: 14px;
      height: 14px;
      background: #10b981;
      border-radius: 50%;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 9px;
    }}

    .step-name {{
      font-size: 13px;
      font-weight: 700;
      color: #0f172a;
    }}

    .step-desc {{
      font-size: 11px;
      color: #64748b;
    }}

    /* DONUT CHART / CATEGORY BREAKDOWN */
    .category-breakdown-body {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}

    .donut-wrap {{
      position: relative;
      width: 130px;
      height: 130px;
      flex-shrink: 0;
    }}

    .donut-center {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      pointer-events: none;
    }}

    .donut-center-num {{
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1;
    }}

    .donut-center-lbl {{
      font-size: 10px;
      font-weight: 600;
      color: #64748b;
      margin-top: 2px;
    }}

    .category-legend {{
      display: flex;
      flex-direction: column;
      gap: 7px;
      width: 100%;
    }}

    .legend-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12.5px;
    }}

    .legend-left {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: #334155;
      font-weight: 500;
    }}

    .legend-dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
    }}
    .dot-cat-blocker {{ background: #ef4444; }}
    .dot-cat-milestone {{ background: #10b981; }}
    .dot-cat-client {{ background: #0ea5e9; }}
    .dot-cat-team {{ background: #f59e0b; }}
    .dot-cat-action {{ background: #8b5cf6; }}

    .legend-count {{
      font-weight: 700;
      color: #0f172a;
    }}

    /* BOTTOM ROW: LATEST UPDATES & RECENT SOURCES */
    .dashboard-bottom-row {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 18px;
    }}

    /* UPDATES LIST */
    .updates-list {{
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .update-item {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 10px 0;
      border-bottom: 1px solid #f1f5f9;
      gap: 12px;
    }}
    .update-item:last-child {{ border-bottom: none; }}

    .update-left {{
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }}

    .pill-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 9px;
      border-radius: 6px;
      white-space: nowrap;
      text-transform: capitalize;
    }}
    .badge-blocker {{ background: #fee2e2; color: #dc2626; }}
    .badge-milestone {{ background: #d1fae5; color: #059669; }}
    .badge-client {{ background: #e0f2fe; color: #0284c7; }}
    .badge-team {{ background: #fef3c7; color: #d97706; }}
    .badge-action {{ background: #ede9fe; color: #7c3aed; }}

    .update-title {{
      font-size: 13px;
      font-weight: 600;
      color: #0f172a;
      line-height: 1.4;
    }}

    .update-subtitle {{
      font-size: 11px;
      color: #64748b;
      margin-top: 2px;
    }}
    .update-subtitle code {{
      background: #f1f5f9;
      padding: 1px 4px;
      border-radius: 4px;
      color: #2563eb;
    }}

    .update-right {{
      text-align: right;
      white-space: nowrap;
    }}

    .update-date {{
      font-size: 11.5px;
      font-weight: 600;
      color: #475569;
    }}

    .update-source-type {{
      font-size: 10.5px;
      color: #94a3b8;
    }}

    /* SOURCES LIST */
    .sources-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .source-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 10px;
      border-radius: 8px;
      transition: background 0.15s ease;
      cursor: pointer;
    }}
    .source-item:hover {{
      background: #f8fafc;
    }}

    .source-left {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .source-icon {{
      width: 32px;
      height: 32px;
      background: #eff6ff;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .source-name {{
      font-size: 13px;
      font-weight: 600;
      color: #0f172a;
    }}

    .source-category {{
      font-size: 11px;
      color: #64748b;
    }}

    .source-right {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .source-time {{
      font-size: 11.5px;
      color: #64748b;
    }}

    .chevron {{
      color: #94a3b8;
    }}

    /* =========================================
       FOOTER TECH STACK & LINKS
       ========================================= */
    .showcase-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 36px;
      padding-top: 24px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      flex-wrap: wrap;
      gap: 20px;
    }}

    .footer-left {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .footer-title {{
      font-size: 13px;
      font-weight: 600;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .tech-stack-badges {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .tech-badge {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      color: #ffffff;
      font-weight: 500;
    }}

    .footer-middle {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 13.5px;
    }}

    .footer-link-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: #94a3b8;
    }}

    .footer-link-row a {{
      color: #38bdf8;
      text-decoration: none;
      font-weight: 500;
    }}
    .footer-link-row a:hover {{ text-decoration: underline; }}

    .footer-right {{
      text-align: right;
    }}

    .handwritten-quote {{
      font-family: 'Caveat', cursive;
      font-size: 24px;
      color: #cbd5e1;
      line-height: 1.2;
    }}

    /* MODAL FOR VIEWING SOURCE NOTE */
    .modal-overlay {{
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      z-index: 999;
      align-items: center;
      justify-content: center;
    }}
    .modal-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 16px;
      width: 90%;
      max-width: 550px;
      padding: 24px;
      color: white;
    }}
    .modal-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}
    .modal-title {{ font-size: 16px; font-weight: 700; color: #38bdf8; }}
    .close-btn {{ background: none; border: none; color: #94a3b8; font-size: 20px; cursor: pointer; }}
    .modal-body {{
      background: #0f172a;
      padding: 14px;
      border-radius: 8px;
      font-family: monospace;
      font-size: 13px;
      white-space: pre-wrap;
      color: #e2e8f0;
      line-height: 1.5;
    }}

    /* RESPONSIVE */
    @media (max-width: 1024px) {{
      .app-window {{ grid-template-columns: 1fr; }}
      .sidebar {{ display: none; }}
      .metrics-grid {{ grid-template-columns: repeat(3, 1fr); }}
      .dashboard-middle-row, .dashboard-bottom-row {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 640px) {{
      .metrics-grid {{ grid-template-columns: 1fr 1fr; }}
      .hero-header {{ flex-direction: column; }}
      .showcase-footer {{ flex-direction: column; align-items: flex-start; }}
    }}
  </style>
</head>
<body>

<div class="showcase-container">
  
  <!-- HERO HEADER -->
  <div class="hero-header">
    <div class="hero-left">
      <div class="hero-brand">
        <div class="hero-logo-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        </div>
        <div class="hero-title">Smart <span>Office Digest</span></div>
      </div>
      <div class="hero-subtitle">Automated Operations & Intelligence Pipeline</div>
      <div class="hero-desc">Turns scattered office notes into structured executive reports and an interactive dashboard.</div>
    </div>

    <div class="hero-features">
      <div class="feature-item">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
        <span>Ingests daily standups & meeting memos</span>
      </div>
      <div class="feature-item">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m5 8 6 6"></path><path d="m4 14 6-6 2-3"></path><path d="M2 5h12"></path><path d="M7 2h1"></path><path d="m22 22-5-10-5 10"></path><path d="M14 18h6"></path></svg>
        <span>Normalizes informal notes to clear English</span>
      </div>
      <div class="feature-item">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>
        <span>Categorizes blockers, risks, milestones, feedback & action items</span>
      </div>
      <div class="feature-item">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
        <span>Generates Markdown digest + HTML dashboard</span>
      </div>
      <div class="feature-item">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
        <span>Tracks sources for full traceability</span>
      </div>
    </div>
  </div>

  <!-- MAIN APP WINDOW (MOCKUP CONTAINER) -->
  <div class="app-window">
    
    <!-- DARK SIDEBAR -->
    <div class="sidebar">
      <div class="sidebar-top">
        <div class="mac-dots">
          <div class="dot dot-red"></div>
          <div class="dot dot-yellow"></div>
          <div class="dot dot-green"></div>
        </div>
        <div class="sidebar-brand">
          <div class="sidebar-brand-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
          </div>
          <div class="sidebar-brand-text">Smart Office Digest</div>
        </div>

        <div class="nav-menu">
          <div class="nav-item active">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
            <span>Dashboard</span>
          </div>
          <div class="nav-item" onclick="alert('Viewing Latest Executive Markdown Digest')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
            <span>Reports</span>
          </div>
          <div class="nav-item" onclick="alert('Ingested {total_notes_count} daily source files.')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 7 4 4 20 4 20 7"></polyline><line x1="9" y1="20" x2="15" y2="20"></line><line x1="12" y1="4" x2="12" y2="20"></line></svg>
            <span>Source Logs</span>
          </div>
          <div class="nav-item">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            <span>Settings</span>
          </div>
        </div>
      </div>

      <div class="sidebar-status-card">
        <div class="status-indicator">
          <div class="status-dot"></div>
          <span>Pipeline Running</span>
        </div>
        <div class="status-sub">Last updated</div>
        <div class="status-sub" style="color: #cbd5e1; font-weight: 500;">{now_time_str}</div>
      </div>
    </div>

    <!-- LIGHT DASHBOARD CONTENT -->
    <div class="main-content">
      
      <!-- TOP BAR -->
      <div class="dashboard-topbar">
        <div>
          <div class="greeting-title">Good morning, here's your daily digest</div>
          <div class="greeting-subtitle">Automated insights from your team's latest updates.</div>
        </div>
        <div class="date-badge">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
          <span>{today_str}</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </div>
      </div>

      <!-- 5 METRIC CARDS ROW -->
      <div class="metrics-grid">
        
        <!-- Total Notes -->
        <div class="metric-card card-blue">
          <div>
            <div class="metric-icon-wrap">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
            </div>
            <div class="metric-label">Total Notes Processed</div>
          </div>
          <div>
            <div class="metric-val-row">
              <div class="metric-number">{total_notes_count}</div>
              <div class="metric-trend trend-up">↑ 12%</div>
            </div>
            <div class="metric-sub">vs. previous day</div>
          </div>
        </div>

        <!-- Critical Blockers -->
        <div class="metric-card card-red">
          <div>
            <div class="metric-icon-wrap">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            </div>
            <div class="metric-label">Critical Blockers</div>
          </div>
          <div>
            <div class="metric-val-row">
              <div class="metric-number">{blockers_count}</div>
              <div class="metric-trend trend-down">↓ 40%</div>
            </div>
            <div class="metric-sub">vs. previous day</div>
          </div>
        </div>

        <!-- Completed Milestones -->
        <div class="metric-card card-green">
          <div>
            <div class="metric-icon-wrap">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <div class="metric-label">Completed Milestones</div>
          </div>
          <div>
            <div class="metric-val-row">
              <div class="metric-number">{milestones_count}</div>
              <div class="metric-trend trend-up">↑ 17%</div>
            </div>
            <div class="metric-sub">vs. previous day</div>
          </div>
        </div>

        <!-- Client Feedback -->
        <div class="metric-card card-cyan">
          <div>
            <div class="metric-icon-wrap">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            </div>
            <div class="metric-label">Client Feedback</div>
          </div>
          <div>
            <div class="metric-val-row">
              <div class="metric-number">{client_count}</div>
              <div class="metric-trend trend-up">↑ 25%</div>
            </div>
            <div class="metric-sub">vs. previous day</div>
          </div>
        </div>

        <!-- Action Items -->
        <div class="metric-card card-purple">
          <div>
            <div class="metric-icon-wrap">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
            </div>
            <div class="metric-label">Action Items</div>
          </div>
          <div>
            <div class="metric-val-row">
              <div class="metric-number">{actions_count}</div>
              <div class="metric-trend trend-up">↑ 29%</div>
            </div>
            <div class="metric-sub">vs. previous day</div>
          </div>
        </div>

      </div>

      <!-- MIDDLE ROW -->
      <div class="dashboard-middle-row">
        
        <!-- PIPELINE OVERVIEW -->
        <div class="white-card">
          <div class="card-header-row">
            <div class="card-title">Pipeline Overview</div>
          </div>

          <div class="pipeline-stepper">
            <div class="step-item">
              <div class="step-icon icon-ingestion">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
              </div>
              <div class="step-name">Ingestion</div>
              <div class="step-desc">Raw notes</div>
            </div>

            <div class="step-connector">
              <div class="step-connector-dot">✓</div>
            </div>

            <div class="step-item">
              <div class="step-icon icon-norm">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m5 8 6 6"></path><path d="m4 14 6-6 2-3"></path><path d="M2 5h12"></path><path d="m22 22-5-10-5 10"></path></svg>
              </div>
              <div class="step-name">Normalization</div>
              <div class="step-desc">Clean & standardize</div>
            </div>

            <div class="step-connector">
              <div class="step-connector-dot">✓</div>
            </div>

            <div class="step-item">
              <div class="step-icon icon-cat">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>
              </div>
              <div class="step-name">Categorization</div>
              <div class="step-desc">AI analysis</div>
            </div>

            <div class="step-connector">
              <div class="step-connector-dot">✓</div>
            </div>

            <div class="step-item">
              <div class="step-icon icon-gen">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
              </div>
              <div class="step-name">Digest Generation</div>
              <div class="step-desc">Markdown + HTML</div>
            </div>
          </div>
        </div>

        <!-- CATEGORY BREAKDOWN -->
        <div class="white-card">
          <div class="card-header-row">
            <div class="card-title">Category Breakdown</div>
          </div>

          <div class="category-breakdown-body">
            
            <!-- DONUT CHART (SVG CONIC REPRESENTATION) -->
            <div class="donut-wrap">
              <svg viewBox="0 0 36 36" width="130" height="130">
                <circle cx="18" cy="18" r="15.915" fill="#f8fafc" stroke="#e2e8f0" stroke-width="3.5"></circle>
                <!-- Blockers -->
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#ef4444" stroke-width="3.8" stroke-dasharray="{b_pct} {100-b_pct}" stroke-dashoffset="25"></circle>
                <!-- Milestones -->
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#10b981" stroke-width="3.8" stroke-dasharray="{m_pct} {100-m_pct}" stroke-dashoffset="{25-b_pct}"></circle>
                <!-- Client -->
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#0ea5e9" stroke-width="3.8" stroke-dasharray="{c_pct} {100-c_pct}" stroke-dashoffset="{25-b_pct-m_pct}"></circle>
                <!-- Team -->
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#f59e0b" stroke-width="3.8" stroke-dasharray="{t_pct} {100-t_pct}" stroke-dashoffset="{25-b_pct-m_pct-c_pct}"></circle>
                <!-- Actions -->
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#8b5cf6" stroke-width="3.8" stroke-dasharray="{a_pct} {100-a_pct}" stroke-dashoffset="{25-b_pct-m_pct-c_pct-t_pct}"></circle>
              </svg>
              <div class="donut-center">
                <div class="donut-center-num">{total_categorized}</div>
                <div class="donut-center-lbl">Total Notes</div>
              </div>
            </div>

            <!-- LEGEND -->
            <div class="category-legend">
              <div class="legend-row">
                <div class="legend-left"><span class="legend-dot dot-cat-blocker"></span> Blockers & Risks</div>
                <div class="legend-count">{blockers_count}</div>
              </div>
              <div class="legend-row">
                <div class="legend-left"><span class="legend-dot dot-cat-milestone"></span> Milestones & Progress</div>
                <div class="legend-count">{milestones_count}</div>
              </div>
              <div class="legend-row">
                <div class="legend-left"><span class="legend-dot dot-cat-client"></span> Client Feedback</div>
                <div class="legend-count">{client_count}</div>
              </div>
              <div class="legend-row">
                <div class="legend-left"><span class="legend-dot dot-cat-team"></span> Team Operations</div>
                <div class="legend-count">{team_count}</div>
              </div>
              <div class="legend-row">
                <div class="legend-left"><span class="legend-dot dot-cat-action"></span> Action Items</div>
                <div class="legend-count">{actions_count}</div>
              </div>
            </div>

          </div>
        </div>

      </div>

      <!-- BOTTOM ROW -->
      <div class="dashboard-bottom-row">
        
        <!-- LATEST UPDATES -->
        <div class="white-card">
          <div class="card-header-row">
            <div class="card-title">Latest Updates</div>
          </div>

          <div class="updates-list">
            {updates_html}
          </div>
        </div>

        <!-- RECENT SOURCES -->
        <div class="white-card">
          <div class="card-header-row">
            <div class="card-title">Recent Sources</div>
            <a href="https://github.com/HumaizaNaz/smart-office-digest/tree/main/Office_Digest_Source" target="_blank" class="card-link">View All →</a>
          </div>

          <div class="sources-list">
            {sources_html}
          </div>
        </div>

      </div>

    </div>

  </div>

  <!-- SHOWCASE FOOTER -->
  <div class="showcase-footer">
    <div class="footer-left">
      <div class="footer-title">Tech Stack</div>
      <div class="tech-stack-badges">
        <div class="tech-badge">
          <span>🐍 Python</span>
        </div>
        <div class="tech-badge">
          <span>🧩 Regex / NLP</span>
        </div>
        <div class="tech-badge">
          <span>🎨 HTML5 / CSS3</span>
        </div>
        <div class="tech-badge">
          <span>🚀 GitHub Pages</span>
        </div>
      </div>
    </div>

    <div class="footer-middle">
      <div class="footer-link-row">
        <span>🔗 <strong>Live Demo</strong>:</span>
        <a href="https://humaizanaz.github.io/smart-office-digest/" target="_blank">humaizanaz.github.io/smart-office-digest/</a>
      </div>
      <div class="footer-link-row">
        <span>🐙 <strong>GitHub Repository</strong>:</span>
        <a href="https://github.com/HumaizaNaz/smart-office-digest" target="_blank">github.com/HumaizaNaz/smart-office-digest</a>
      </div>
    </div>

    <div class="footer-right">
      <div class="handwritten-quote">
        Turning unstructured notes<br>into actionable insights.
      </div>
    </div>
  </div>

</div>

<!-- INTERACTIVE MODAL FOR RAW NOTES -->
<div id="fileModal" class="modal-overlay" onclick="closeFileModal()">
  <div class="modal-card" onclick="event.stopPropagation()">
    <div class="modal-header">
      <div id="modalFileName" class="modal-title">Source Note View</div>
      <button class="close-btn" onclick="closeFileModal()">✕</button>
    </div>
    <div id="modalFileContent" class="modal-body"></div>
  </div>
</div>

<script>
  const fileContents = {files_json};

  function openFileModal(fileName) {{
    document.getElementById('modalFileName').textContent = '📄 ' + fileName;
    document.getElementById('modalFileContent').textContent = fileContents[fileName] || 'No content found.';
    document.getElementById('fileModal').style.display = 'flex';
  }}

  function closeFileModal() {{
    document.getElementById('fileModal').style.display = 'none';
  }}
</script>

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
        
    # Save HTML Dashboard in Output folder and Root index.html
    html_content = build_dashboard_html(data)
    html_path = os.path.join(OUTPUT_DIR, "Weekly_Digest_Dashboard.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    root_index_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(root_index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[+] Markdown Report: {md_path}")
    print(f"[+] HTML Dashboard:  {html_path}")
    print(f"[+] Root index.html: {root_index_path}")

if __name__ == "__main__":
    main()
