# n8n lineOArag Workflow

RAG-powered LINE chatbot for village management (นิติบุคคลหมู่บ้าน). Handles visitor registration (Smart Ticket), complaint management with priority classification, and general Q&A using village documents.

## Architecture

```
LINE ──► n8n (lineOArag workflow) ──► Supabase (vector store + Django DB)
                │
                └──► Replies via LINE Messaging API
```

### Credentials Needed (set via .env)
| Credential | .env Variable | n8n Type |
|---|---|---|
| LINE Messaging API | `LINE_CHANNEL_ACCESS_TOKEN` | `lineMessagingApi` |
| Google Gemini API | `GEMINI_API_KEY` | `googlePalmApi` |
| Supabase Vector Store | `SUPABASE_VECTOR_*` | `supabaseApi` |
| Supabase Django DB | `SUPABASE_DJANGO_*` | `supabaseApi` |

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Setup

1. **Clone and configure**
   ```bash
   git clone <repo-url> n8n-lineoa
   cd n8n-lineoa
   cp .env.example .env
   # Edit .env with your actual API keys and credentials
   ```

2. **Start n8n + PostgreSQL**
   ```bash
   docker compose up -d
   ```
   n8n will be available at `http://localhost:5678`

3. **Import workflow**
   - Open n8n in browser
   - Go to **Workflows** → **Import from File**
   - Select `workflows/lineOArag.json`

4. **Set up credentials in n8n**
   - After importing, click each missing credential and fill:
     - **Line Messaging account**: paste `LINE_CHANNEL_ACCESS_TOKEN`
     - **Google Gemini(PaLM) Api account**: paste `GEMINI_API_KEY`
     - **Supabase account 2** (vector store): host + service role
     - **Supabase - Django DB** (app data): host + service role

5. **Activate the workflow**

## Workflow Nodes (22 total)

| Node | Purpose |
|---|---|
| Line Messaging Trigger | Receives incoming LINE messages |
| AI Agent + Google Gemini | Intent classification + priority (critical/high/medium/low) |
| Structured Output Parser | Parses agent JSON output |
| Switch | Routes by intent (visitor / complaint / general) |
| Line Messaging QR | Sends Smart Ticket QR with visitor info |
| Store Visitor Log | INSERT into `visit_logs` |
| Store Issue | INSERT into `issues_issue` |
| Store Complaint Record | INSERT into `issues_complaint` |
| Create Admin Notification | INSERT into `notifications_notification` |
| Line Messaging chat | Sends complaint confirmation |
| Complaint Reply | Sends confirmation via LINE |
| Supabase Vector Store | RAG: stores/retrieves document embeddings |
| Embeddings (Gemini) | Generates text embeddings |
| Google Gemini Chat Model | LLM for AI Agent |
| Simple Memory | Conversation context (5-turn window) |

## Database Schema

See `implementation_plan.md` for full SQL schema including:
- `visit_logs` table (visitor registration)
- `issues_issue` + `issues_complaint` (complaint management)
- `notifications_notification` (admin alerts)

## Project Structure

```
.
├── docker-compose.yml       # n8n + PostgreSQL 16
├── .env                     # Credentials (git-ignored)
├── .env.example             # Template for .env
├── .gitignore
├── README.md
├── implementation_plan.md   # Full design doc
├── workflow_n8n.md          # Node-by-node documentation
└── workflows/
    └── lineOArag.json       # Exported workflow (importable)
```
