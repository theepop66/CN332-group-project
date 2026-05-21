<div align="center">

<img src="Documents/LOGO/baanhao_logo.png" alt="drawing" width="200"/>

# **BaanHao: Smart Living Management System**
## **CN332 Object-Oriented Analysis and Design Project**

<div align="left">

---

# Project Overview

BaanHao is a comprehensive property management platform tailored for housing estates and condominiums. It is engineered to optimize the operational efficiency of juristic persons while significantly enhancing the residential experience.

From an administrative standpoint, the platform focuses on streamlining redundant workflows. It resolves persistent issues such as repetitive handling of basic inquiries and the mismanagement of fragmented or unrecorded complaints.

Simultaneously, for residents, BaanHao is designed to eliminate traditional communication barriers, emphasizing seamless accessibility and rapid response times.

---

# Key Features

### For Residents (via LINE Official Account)
- **RAG-Powered Q&A:** AI chatbot answers questions about community rules, fees, and regulations by retrieving information from an uploaded knowledge base (PDF/CSV) stored in a Supabase vector store, powered by Google Gemini 2.5 Flash Lite.
- **Smart Ticket (Visitor Registration):** Residents register guests via LINE chat by providing a visitor name and license plate number. The bot validates the input and sends back a QR code Smart Ticket automatically.
- **Complaint Filing:** Residents report issues (e.g., broken lights, water pipe leaks, noise) by chatting with the bot. The AI collects subject, location, and description, then classifies priority (critical / high / medium / low) and stores the complaint directly into the Django database — triggering an admin notification on the web dashboard.
- **Conversational Memory:** The bot maintains a 5-turn conversation window per LINE user, enabling multi-step data collection without re-asking previous answers.

### For Juristic Person (via Web Application)
- **Dashboard:** A central command hub providing a real-time overview of the system's status, recent activities, and key operational metrics at a glance.
- **All Task (Complaint & Maintenance):** A comprehensive task management module categorizing resident complaints and maintenance requests. Staff can track progress, update ticket statuses, and manage workflows efficiently.
- **Notice:** An announcement management system allowing staff to create, edit, and broadcast important community notices directly to residents.
- **Event:** A feature to organize, schedule, and promote community events or activities to encourage resident engagement.
- **Staff:** A role and account management system for juristic personnel, enabling administrators to control access levels and staff responsibilities securely.
- **Analytics:** In-depth data visualization and reporting tools that analyze task resolution times, frequent issues, and overall operational efficiency to aid in data-driven decision-making.

---

# LINE OA Chatbot — RAG Architecture

The LINE OA chatbot is built on **n8n** (self-hosted via Docker) and uses a **RAG (Retrieval-Augmented Generation)** pipeline to answer resident inquiries from community documents.

### System Flow

```
Resident (LINE)
    │
    ▼
LINE Messaging Trigger (n8n)
    │
    ▼
AI Agent ── Google Gemini 2.5 Flash Lite (LLM)
    │     ├── Supabase Vector Store (RAG knowledge base)
    │     ├── Simple Memory (5-turn conversation window)
    │     └── Structured Output Parser (JSON intent classification)
    │
    ▼
Switch Router (by intent)
    │
    ├─── visitor ──► Send Smart Ticket QR via LINE → Save to visit_logs (Supabase)
    │
    ├─── complaint ► Save to issues_issue + issues_complaint → Notify admin dashboard
    │                └─► Reply confirmation via LINE
    │
    └─── general ──► RAG retrieval from vector store → Answer via LINE
```

### Intent Classification

| Intent | Trigger | Output |
|---|---|---|
| `visitor` | Resident wants to register a guest | Smart Ticket QR code (name + license plate) |
| `complaint` | Resident reports an issue | Stored complaint with priority (critical / high / medium / low) + admin notification |
| `general` | Any question about village rules/info | RAG-based answer from community documents |

### RAG Knowledge Base Setup

Documents (PDF/CSV) are uploaded via an n8n web form → chunked → embedded with `gemini-embedding-001` → stored in Supabase vector store. On each user query, the AI Agent retrieves relevant chunks before generating a response.

### Integration with Django Dashboard

All data from LINE interactions flows directly into the Django web application database (Supabase PostgreSQL):
- Complaints appear in the **All Tasks** module with priority labels
- Visitor logs are stored in `visit_logs` table
- Admin receives in-app notifications for every new complaint

### Setup

```bash
cd n8n-LineOA
cp .env.example .env   # fill in LINE token, Gemini API key, Supabase credentials
docker compose up -d   # starts n8n at http://localhost:5678
# Import workflows/lineOArag.json in n8n UI → Activate
```

---

# Technical Stack

### Frontend (Juristic Web Application)
- **Core Languages:** ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

### Backend & API
- **Framework:** ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
- **Messaging API:** ![LINE](https://img.shields.io/badge/LINE-00C300?style=for-the-badge&logo=line&logoColor=white) 

### Database
- **Relational Database:** ![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

### LINE OA Chatbot (RAG Workflow)
- **Workflow Automation:** ![n8n](https://img.shields.io/badge/n8n-%23EA4B71.svg?style=for-the-badge&logo=n8n&logoColor=white)
- **LLM & Embeddings:** ![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white) `gemini-2.5-flash-lite` + `gemini-embedding-001`
- **Vector Store:** ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)

### Tools & Management
- **Design & Prototyping:** ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white) 
- **Version Control:** ![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
- **Project Management:** ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) 

---

| Project Progress | Doc & Slides | Presentation Date |
|---|---|---|
| **Week 1: Concept** | [📄 Concept Paper](Documents/Iteration1/hm1_CONCEPT_PAPER.pdf) <br> [📊 Iteration 1 Slides](Documents/Iteration1/iteration1-BaanHao.pdf) |-|
| **Week 2: Requirements** | [📄 การแจกแจง Requirement](Documents/Iteration2/hm2_การแจกแจงrequirement.pdf) <br> [📊 Iteration 2 Slides](Documents/Iteration2/iteration2-BaanHao.pdf) |-|
| **Week 3: Development** | [🎨 Canva Link](https://www.canva.com/design/DAG-12vJwHI/FFv4AjDZGIT0hqmoKelIXQ/view?utm_content=DAG-12vJwHI&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h50f6ef177b) <br> [📊 Iteration 3 Slides](Documents/Iteration3/Iteration3_BannHao.pdf) | 26/01/2026 |
| **Week 4: UX/UI Demo** | [🎥 GUI Website Walkthrough](https://youtu.be/igLxI9eYJGI?si=iCysm1rsU2UA-4bB) <br> [📱 Line OA Short Demo](https://youtube.com/shorts/j89uEZ3Yu6c?feature=share) |-|
| **Week 5: Facade Pattern in project** | [📊 Iteration 5 Slides](https://www.canva.com/design/DAHAvvavFFM/HOUiDaKPhY2ek7LEpf9VWA/view?utm_content=DAHAvvavFFM&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=he9fad04ba6) <br> [📄 Iteration 5-7 PDF](Documents/Iteration5-7/BaanHao-Iteration5-7.pdf) |-|
| **Week 6: Log in interface** | [📊 Iteration 6 Slides](https://www.canva.com/design/DAHBRznlkXk/oznuqUfk21gcsGM5xwXzZg/edit?utm_content=DAHBRznlkXk&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) <br> [📄 Iteration 5-7 PDF](Documents/Iteration5-7/BaanHao-Iteration5-7.pdf) |-|
| **Week 7: Implement plan** | [📊 Iteration 7 Slides](https://www.canva.com/design/DAHDLQnATVE/9BKB05CxdQyN2q5MyVqCfg/edit?utm_content=DAHDLQnATVE&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) <br> [📄 Iteration 5-7 PDF](Documents/Iteration5-7/BaanHao-Iteration5-7.pdf) |-|
| **Week 8 - 9: Development** | [📊 Iteration 5-7 Slides (PDF)](Documents/Iteration5-7/BaanHao-Iteration5-7.pdf) |-|
| **Week 10 - 11: Development** | [🎥 GUI Website Walkthrough](https://youtu.be/igLxI9eYJGI?si=iCysm1rsU2UA-4bB) <br> [📱 Line OA Demo](https://youtube.com/shorts/j89uEZ3Yu6c?feature=share) |-|
| **Week 12 - Final: Testing and Final** | [📄 Final Presentation (PDF)](Documents/Final_Presentation_CN332.pdf) <br> [📊 Use Case Diagram](Documents/Usecase_Diagram/) <br> [📊 Class Diagram](Documents/Database_Diagram/BaanHao_Diagram\(version-1\).pdf) | 18/05/2026|

---

## Instructor Feedback Log

> [!IMPORTANT]
> **Date: 26/01/2026 (Iteration 1-3)**
> - **Comment:** ให้ดูตัวอย่างการสืบทอด Class (Inheritance) ที่ยืดหยุ่นมากขึ้น เพื่อให้ Code Clean และจัดการ Logic ได้ง่ายขึ้น

---

# Project Trackability

Our team uses **GitHub Projects** (Kanban Board) to manage tasks, sprints, and overall project progress following Agile methodologies. This ensures transparent collaboration and efficient workflow management.

* **Project Board:** [View our Kanban Board Here](https://github.com/users/theepop66/projects/3/views/3)

### Project Status

![Open Issues](https://img.shields.io/github/issues/theepop66/CN332-group-project)
![Closed Issues](https://img.shields.io/github/issues-closed/theepop66/CN332-group-project)

### Task Distribution by Member

> Tasks breakdown per team member (Backlog / In Progress / Done)

![Task Distribution](Documents/image_project_track/image2.png)

| Team Member | Total Issues | ✅ Done | PRs Merged | Commits |
| :--- | :---: | :---: | :---: | :---: |
| @athiphat67 | 31 | 31 | 40 | 118 |
| @theepop66 | 25 | 25 | 2 | 10 |
| @6710615185 | 24 | 24 | 2 | 20 |
| @panifield | 16 | 16 | 8 | 15 |
| @napattiral276 | 15 | 15 | 2 | 8 |

* Latest Update 21 May 2026 — All 44 issues closed (100%)


# Software Design Artifacts

### 1. System Modeling (UML Diagrams)
* **Use Case Diagram:** [📊 View Use Case Diagrams](Documents/Usecase_Diagram/)
* **Class Diagram:** [📊 BaanHao Class Diagram (PDF)](Documents/Database_Diagram/BaanHao_Diagram\(version-1\).pdf)

### 2. Database Design
* **Entity Relationship Diagram (ERD):** [📊 BaanHao Database Diagram (PDF)](Documents/Database_Diagram/BaanHao_Diagram\(version-1\).pdf) *(Covered in Class Diagram)*

### 3. User Interface (UI) & User Experience (UX)
* **System Wireframes & Mockups:** [🖼️ View Website Mockups](Documents/Iteration4/website/) · [📱 LINE OA Mockup](Documents/Iteration4/LineOA/LineOA_Chatbot.png)

---

# Installation

### Prerequisites 
- **Git**
- **Terminal**

### Step-by-Step Installation

**1. Clone the repository:**
```bash
git clone https://github.com/theepop66/CN332-group-project.git CN332
cd CN332/myproject
```

**2. Create and activate a virtual environment:**
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirement.txt
```

**4. Environment Variables Setup:**
```bash
# about .env file. Let talk to Back-end Team :)
```

**5. Database Setup & Migration:**
```bash
# about database file. Let talk to Back-end Team :)
```

**6. Run the development server:**
```bash
cd baanhao_project

python manage.py runserver

# Note: When you run server successfully, you can click http://127.0.0.1:8000/ to use the web application.
```

**7. Test Account :**
```bash
Username : admin
Password : admin12345
```
---

# Project Structure
```markdown
CN332-group-project/              # Root directory of the project
├── BannHao_CLI/                  # Command Line Interface module (if applicable)
├── Documents/                    # All project documentation and assets
│   ├── Database_Diagram/         # Class diagram and database design files
│   ├── Iteration1/               # Documents and slides for Week 1
│   ├── Iteration2/               # Documents and slides for Week 2
│   ├── Iteration3/               # Documents and slides for Week 3
│   ├── Iteration4/               # UI mockups and LINE OA screenshots
│   ├── Iteration5-7/             # Combined slides for Iterations 5-7
│   ├── Usecase_Diagram/          # System use case diagram images
│   ├── image_project_track/      # Project tracking screenshots
│   └── LOGO/                     # Project logo image files
├── myproject/                    # Main development folder (Source Code)
│   ├── baanhao_project/          # Main Django project directory containing all apps
│   │   ├── analytics/            # Django App: Data processing and statistics
│   │   ├── baanhao_project/      # Django core configuration (settings.py, urls.py)
│   │   ├── complaints/           # Django App: Resident complaint management
│   │   ├── dashboard/            # Django App: Juristic admin dashboard UI/Logic
│   │   ├── issues/               # Django App: General issues and ticketing system
│   │   ├── maintenance/          # Django App: Maintenance request management
│   │   ├── media/profile_images/ # Directory for user-uploaded media (e.g., profile pics)
│   │   ├── notifications/        # Django App: Notification system & LINE API integration
│   │   ├── profile_images/       # (Fallback/Default directory for profile pictures)
│   │   ├── properties/           # Django App: Property and asset management
│   │   ├── static/               # Directory for static files (CSS, JavaScript, Images)
│   │   ├── templates/            # Directory for HTML templates (Frontend UI)
│   │   ├── users/                # Django App: User management, authentication, and roles
│   │   ├── .env.example          # Template for environment variables (e.g., DB credentials)
│   │   ├── db.sqlite3            # Default SQLite database for local development
│   │   └── manage.py             # Django command-line utility (runserver, migrate, etc.)
│   ├── .gitignore                # Git ignore file for the source code level (e.g., venv)
│   └── requirement.txt          # Python dependencies list (e.g., django, psycopg2)
├── .gitignore                    # Root level Git ignore file
└── README.md                     # The main project documentation file (this file)
```

---

## Team Members

| Student ID | Name | Roles |
| :---: | :--- | :--- |
| `6710615292` | athiphat sunsit | Team lead , Front-end, Back-end, QA |
| `6710615185` | ภูริช อัมพะวา | Front-end, Back-end |
| `6710545010` | นพัตธีรา เหลาเกิ้มหุ่ง | Front-end |
| `6710615144` | ปณิธาน ตันตื้อ | Front-end |
| `6710685014` | ธีภพ รัตนทรัพย์ศิริ | AI RAG, Line OA Back-end |

