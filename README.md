# 🏢 Executive Office Digest — Autonomous Operations & Intelligence Agent

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Completed-success)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **An automated pipeline and agent that ingests raw, decentralized daily office logs, meeting notes, client feedback, and blocker memos—synthesizing them into structured, executive-ready digests and interactive dashboards.**

---

## 📌 Problem Statement
In fast-paced engineering and product teams, critical updates are often scattered across disparate channels (daily standups, client chats, bug trackers, and meeting notes). Executives and project leads spend hours manually consolidating this information to assess risks, track deliverables, and align cross-functional teams.

## 💡 Solution
**Executive Office Digest** provides a lightweight, automated pipeline that:
1. **Ingests** unstructured daily notes from local and shared sources.
2. **Parses & Translates** multi-lingual notes (e.g., Roman Urdu/Hindi) into standardized, corporate-grade English.
3. **Categorizes** logs into critical business pillars:
   - ⚠️ **Blockers & High-Priority Risks**
   - 🚀 **Milestones & Progress Highlights**
   - 💬 **Client Requirements & Feedback**
   - 👥 **Team Operations & Standup Notes**
   - 📋 **Action Items & Accountability Checklists**
4. **Exports** clean Executive Markdown digests and modern, responsive **HTML Dashboards**.

---

## 🏗️ Architecture & Workflow

```
┌───────────────────────────────┐
│     Raw Office Inputs         │
│  (Daily Notes, Memos, Text)   │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│   Digest Engine & Parser      │
│  - Ingestion & Normalization  │
│  - Multi-Lingual Translation  │
│  - Heuristic Classification   │
└──────────────┬────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐┌──────────────┐
│  Executive   ││ Modern Web   │
│ Markdown Doc ││ HTML UI      │
└──────────────┘└──────────────┘
```

---

## 🚀 Key Features
- **Zero Configuration Run:** Automatically detects new notes added to the source folder.
- **Dynamic Translation & Normalization:** Intelligently maps informal team shorthand into executive English.
- **Risk Mitigation Matrix:** Formats blockers with dates, root cause descriptions, and source traceability.
- **Interactive Action Checklist:** Generates browser-ready checkboxes for team accountability.
- **Multi-Format Distribution:** Produces standalone `.md` reports for Slack/Notion and `.html` dashboards for web viewing.

---

## 🛠️ Tech Stack
- **Language:** Python 3
- **Core Modules:** `re`, `os`, `glob`, `datetime`
- **Frontend / UI:** Modern CSS3 (CSS Variables, Flexbox, CSS Grid) & HTML5
- **Export Formats:** Markdown (`.md`), Interactive Web Dashboard (`.html`)

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/executive-office-digest.git
cd executive-office-digest
```

### 2. Add your daily notes
Drop your `.txt` or `.md` notes into `Office_Digest_Source/`:
```text
Date: 22 Sept
- Payment gateway documentation received, integration unblocked
- Client approved revised blue color palette
- Action: Deploy staging build on Monday
```

### 3. Generate the Digest
```bash
python generate_digest.py
```

### 4. View Results
- **Markdown Digest:** [`Office_Digest_Output/Weekly_Digest_Latest.md`](Office_Digest_Output/Weekly_Digest_Latest.md)
- **HTML Dashboard:** Open [`Office_Digest_Output/Weekly_Digest_Dashboard.html`](Office_Digest_Output/Weekly_Digest_Dashboard.html) in any browser.

---

## 📊 Sample Output Preview

```markdown
# 🏢 Weekly Executive Office Digest
*Generated: 2026-09-24 | Ingested Logs: 7*

## ⚠️ Critical Blockers & Risks
| Date | Issue / Risk Description | Source |
| :--- | :--- | :--- |
| 18 Sept | Payment gateway delay reported | `2025-09-18_Blocker.txt` |
| 18 Sept | Launch date may slip by 1 week | `2025-09-18_Blocker.txt` |

## 🚀 Progress & Key Achievements
- [19 Sept] Fixed 3 major critical bugs in the mobile application.
- [19 Sept] QA team initiated full regression testing.
- [22 Sept] Action Item: Deploy staging build on Monday morning.
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
