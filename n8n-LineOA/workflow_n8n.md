# n8n Workflow Report: `lineOArag`

## Overview

| Property | Value |
|----------|-------|
| **Workflow ID** | `yAKmq3QBkU0tatqe` |
| **Name** | lineOArag |
| **Status** | Active |
| **Total Nodes** | 22 |
| **Created** | 2026-02-06 |
| **Last Updated** | 2026-05-13 |
| **Trigger** | LINE Messaging (Incoming Messages) |

---

## Purpose

LINE chatbot for a residential village (หมู่บ้าน) management system. Residents can chat via LINE and the bot handles three types of requests:
1. **Visitor registration** — Register guests with name + license plate → Smart Ticket QR code
2. **Complaint reporting** — Log complaints with subject, location, description → stored in database
3. **General inquiries** — Answer questions about village rules via RAG

All data is stored in Supabase for viewing in the Django admin dashboard.

---

## Architecture Diagram

```
LINE Message
    │
    ▼
Line Messaging Trigger
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                    AI Agent                          │
│  (Gemini 2.5 Flash Lite + Structured Output Parser) │
│  Intent: visitor | complaint | general              │
│  + Priority classification for complaints           │
└─────────────────────────────────────────────────────┘
    │
    ▼
    Switch (routes by intent)
    │
    ├─── Route 0: is_ticket_ready ────────────────────┐
    │                                                 ▼
    │                                      Line Messaging QR
    │                                      (sends Smart Ticket Flex)
    │                                                 ▼
    │                                      Store Visitor Log
    │                                      (Supabase INSERT visit_logs)
    │
    ├─── Route 1: is_complaint_ready ────────────────┐
    │                                                 ▼
    │                                      Store Issue
    │                                      (Supabase INSERT issues_issue)
    │                                                 ▼
    │                                      Store Complaint Record
    │                                      (Supabase INSERT issues_complaint)
    │                                                 ▼
    │                                      Create Admin Notification
    │                                      (Supabase INSERT notifications)
    │                                                 ▼
    │                                      Complaint Reply
    │                                      (LINE reply with AI response)
    │
    └─── Route 2: intent = "general" ────────────────┐
                                                      ▼
                                              Line Messaging chat
                                              (LINE reply with AI response)
```

---

## Node Details

### Section 1: RAG — Load Data Flow (Upload Documents)

These nodes handle document upload for the RAG (Retrieval-Augmented Generation) knowledge base.

#### 1.1 Upload your file here

| Property | Value |
|----------|-------|
| **Type** | `n8n-nodes-base.formTrigger` |
| **Position** | (-128, 0) |
| **Purpose** | Web form trigger for uploading CSV/PDF documents |

**Parameters:**
- Form title: "Upload your data to test RAG"
- Accepts: `.pdf`, `.csv`

#### 1.2 Default Data Loader

| Property | Value |
|----------|-------|
| **Type** | `@n8n/n8n-nodes-langchain.documentDefaultDataLoader` |
| **Position** | (320, 160) |
| **Purpose** | Loads uploaded CSV data into documents |

**Parameters:**
- Data type: binary
- Loader: CSV Loader

#### 1.3 Supabase Vector Store

| Property | Value |
|----------|-------|
| **Type** | `@n8n/n8n-nodes-langchain.vectorStoreSupabase` |
| **Position** | (112, 0) |
| **Credentials** | Supabase account 2 (vector store project) |
| **Purpose** | Stores document embeddings for RAG retrieval |

**Parameters:**
- Mode: insert
- Table: `documents`

#### 1.4 Embeddings

| Property | Value |
|----------|-------|
| **Type** | `@n8n/n8n-nodes-langchain.embeddingsGoogleGemini` |
| **Position** | (512, 480) |
| **Credentials** | Google Gemini(PaLM) Api account |
| **Purpose** | Generates embeddings for vector search |

**Parameters:**
- Model: `models/gemini-embedding-001`

---

### Section 2: RAG — Retriever Flow (Question Answering)

#### 2.1 Google Gemini Chat Model

| Property | Value |
|----------|-------|
| **Type** | `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` |
| **Position** | (672, 240) |
| **Credentials** | Google Gemini(PaLM) Api account |
| **Purpose** | LLM for the AI Agent |

**Parameters:**
- Model: `models/gemini-2.5-flash-lite`
- Retry on fail: Yes (5 retries, 2s apart)

#### 2.2 Supabase vector search

| Property | Value |
|----------|-------|
| **Type** | `@n8n/n8n-nodes-langchain.vectorStoreSupabase` |
| **Position** | (960, 256) |
| **Credentials** | Supabase account 2 |
| **Purpose** | Retrieves relevant documents as tool for AI Agent |

**Parameters:**
- Mode: retrieve-as-tool
- Table: `documents`

#### 2.3 Simple Memory

| Property | Value |
|----------|-------|
| **Type** | `@n8n/n8n-nodes-langchain.memoryBufferWindow` |
| **Position** | (832, 240) |
| **Purpose** | Maintains conversation context (last 5 messages) |

**Parameters:**
- Session key: `{{ $('Line Messaging Trigger').item.json.source.userId }}`
- Context window: 5

#### 2.4 Structured Output Parser

| Property | Value |
|----------|-------|
| **Type** | `@n8n/n8n-nodes-langchain.outputParserStructured` |
| **Position** | (1248, 256) |
| **Purpose** | Parses AI output into structured JSON |

**Schema:**
```json
{
  "intent": "string",
  "is_ticket_ready": "boolean",
  "is_complaint_ready": "boolean",
  "visitor_name": "string",
  "license_plate": "string",
  "complaint_subject": "string",
  "complaint_location": "string",
  "complaint_description": "string",
  "complaint_priority": "string",
  "reply": "string"
}
```

---

### Section 3: Main Chatbot Flow

#### 3.1 Line Messaging Trigger

| Property | Value |
|----------|-------|
| **Type** | `@aotoki/n8n-nodes-line-messaging.lineMessagingTrigger` |
| **Position** | (672, -16) |
| **Credentials** | Line Messaging account |
| **Purpose** | Receives incoming LINE messages from residents |

**Parameters:**
- Events: message

#### 3.2 AI Agent

| Property | Value |
|----------|-------|
| **Type** | `@n8n/n8n-nodes-langchain.agent` |
| **Position** | (944, -16) |
| **Tools** | Supabase vector search (RAG) |
| **Memory** | Simple Memory (buffer window, 5 messages) |
| **Output Parser** | Structured Output Parser |
| **Language Model** | Google Gemini Chat Model |

**Full Prompt (Thai):**
```
คุณคือ "ผู้ช่วยนิติบุคคลหมู่บ้าน" หน้าที่ของคุณคือคัดกรองความต้องการของลูกบ้าน (Intent Classification)

กฎการทำงาน:
1. การระบุเจตนา (Intent) ให้ตั้งค่า intent ตามเจตนา:
   - 'visitor': ลูกบ้านต้องการลงทะเบียนคนมาหา
   - 'complaint': ลูกบ้านต้องการแจ้งปัญหา/ร้องเรียน (เช่น ไฟเสีย, ท่อแตก, เสียงดัง)
   - 'general': ถามคำถามทั่วไปเกี่ยวกับหมู่บ้าน

2. เงื่อนไข Smart Ticket (intent: 'visitor'):
   - ต้องได้ "ชื่อและนามสกุลจริง" และ "ทะเบียนรถ" ครบถ้วนเท่านั้น
   - หากครบแล้ว ให้ตั้งค่า is_ticket_ready = true
   - หากข้อมูลไม่ครบให้ถามจนกว่าจะได้ข้อมูลจนครบ

3. เงื่อนไขการรับเรื่องร้องเรียน (intent: 'complaint'):
   - ต้องเก็บข้อมูล 3 อย่าง: "หัวข้อ", "สถานที่เกิดเหตุ", และ "รายละเอียด"
   - หากครบแล้ว ให้ตั้งค่า is_complaint_ready = true
   - หากข้อมูลไม่ครบ ให้ถามลูกบ้านอย่างสุภาพเพื่อขอข้อมูลที่ขาดไป

4. การตอบคำถามทั่วไป (intent: 'general'):
   - ใช้เครื่องมือ Supabase vector search เพื่อค้นหาข้อมูลกฎระเบียบและตอบกลับ

5. การจัดลำดับความสำคัญของข้อร้องเรียน (Complaint Priority):
   - วิเคราะห์เนื้อหาข้อร้องเรียนและกำหนด priority:
     - 'critical': เหตุฉุกเฉินที่ต้องดำเนินการทันที (เช่น ไฟไหม้, ก๊าซรั่ว, อุบัติเหตุร้ายแรง)
     - 'high': ปัญหารุนแรงที่ต้องดำเนินการด่วน (เช่น ไฟดับทั้งหมู่บ้าน, ท่อประปาแตก, เหตุทะเลาะวิวาท)
     - 'medium': ปัญหาทั่วไปที่ต้องดำเนินการภายใน 1-2 วัน (เช่น ไฟถนนเสีย, เสียงรบกวน)
     - 'low': ปัญหาเล็กน้อยที่สามารถรอได้ (เช่น ต้นไม้รก, สุนัขเห่า)
   - ค่าเริ่มต้น: 'medium' หากไม่แน่ใจ

ข้อมูลจากลูกบ้าน: {{ $('Line Messaging Trigger').item.json.message.text }}
```

#### 3.3 Switch (Router)

| Property | Value |
|----------|-------|
| **Type** | `n8n-nodes-base.switch` |
| **Position** | (1312, -16) |
| **Purpose** | Routes based on classified intent |

**Routing Rules:**

| Route | Condition | Destination |
|-------|-----------|-------------|
| **0** | `$json.output.is_ticket_ready` = true | Line Messaging QR → Store Visitor Log |
| **1** | `$json.output.is_complaint_ready` = true | Store Issue → Store Complaint Record → Create Admin Notification → Complaint Reply |
| **2** | `$json.output.intent` = "general" | Line Messaging chat |
| **3** | (unused) | — |
| **4** | (unused) | — |

#### 3.4 Line Messaging QR

| Property | Value |
|----------|-------|
| **Type** | `@aotoki/n8n-nodes-line-messaging.lineMessaging` |
| **Position** | (1728, -144) |
| **Credentials** | Line Messaging account |
| **Purpose** | Sends Smart Ticket QR code via LINE Flex Message |

**Output chain:** → Store Visitor Log

#### 3.5 Line Messaging chat

| Property | Value |
|----------|-------|
| **Type** | `@aotoki/n8n-nodes-line-messaging.lineMessaging` |
| **Position** | (1728, 176) |
| **Credentials** | Line Messaging account |
| **Purpose** | Sends text reply for general inquiries |

---

### Section 4: New — Database Storage Nodes (Added 2026-05-13)

All 5 nodes use **Supabase - Django DB** credentials (the Django app's Supabase project).

#### 4.1 Store Visitor Log

| Property | Value |
|----------|-------|
| **Type** | `n8n-nodes-base.supabase` |
| **Position** | (1952, -400) |
| **Operation** | Create a new row |
| **Table** | `visit_logs` |

**Field Mapping:**

| Column | Value |
|--------|-------|
| `visitor_name` | `{{ $("Switch").item.json.output.visitor_name }}` |
| `license_plate` | `{{ $("Switch").item.json.output.license_plate }}` |
| `line_user_id` | `{{ $("Line Messaging Trigger").item.json.message.source.userId }}` |
| `status` | `pending` |
| `created_at` | `{{ $now }}` |

#### 4.2 Store Issue

| Property | Value |
|----------|-------|
| **Type** | `n8n-nodes-base.supabase` |
| **Position** | (1728, 50) |
| **Operation** | Create a new row |
| **Table** | `issues_issue` |

**Field Mapping:**

| Column | Value |
|--------|-------|
| `title` | `{{ $("Switch").item.json.output.complaint_subject }}` |
| `description` | `{{ $("Switch").item.json.output.complaint_description }}` |
| `location` | `{{ $("Switch").item.json.output.complaint_location }}` |
| `priority` | `{{ $("Switch").item.json.output.complaint_priority }}` |
| `status` | `pending` |
| `created_date` | `{{ $now }}` |
| `reporter_line_id` | `{{ $("Line Messaging Trigger").item.json.message.source.userId }}` |
| `analysis_json` | `=({"source":"line_chatbot"})` (parenthesized to ensure valid JS object eval) |

#### 4.3 Store Complaint Record

| Property | Value |
|----------|-------|
| **Type** | `n8n-nodes-base.supabase` |
| **Position** | (1952, 50) |
| **Operation** | Create a new row |
| **Table** | `issues_complaint` |

**Field Mapping:**

| Column | Value |
|--------|-------|
| `issue_ptr_id` | `{{ $json.id }}` (from preceding Store Issue node) |
| `category` | `general` |

#### 4.4 Create Admin Notification

| Property | Value |
|----------|-------|
| **Type** | `n8n-nodes-base.supabase` |
| **Position** | (2176, 50) |
| **Operation** | Create a new row |
| **Table** | `notifications_notification` |

**Field Mapping:**

| Column | Value |
|--------|-------|
| `title` | `New complaint: {{ $("Switch").item.json.output.complaint_subject }}` |
| `message` | `Priority: {{ $("Switch").item.json.output.complaint_priority }} - {{ $("Switch").item.json.output.complaint_description }}` |
| `created_at` | `{{ $now }}` |

#### 4.5 Complaint Reply

| Property | Value |
|----------|-------|
| **Type** | `@aotoki/n8n-nodes-line-messaging.lineMessaging` |
| **Position** | (2176, 300) |
| **Credentials** | Line Messaging account |
| **Purpose** | Sends AI-generated reply back to LINE user for complaints |

**Field Mapping:**
- `to`: `{{ $("Line Messaging Trigger").item.json.source.userId }}`
- `text`: `{{ $("Switch").item.json.output.reply }}`

---

## Connection Map

### Complete Node Connections

```
Line Messaging Trigger
  └─ main → AI Agent

AI Agent
  ├─ main → Switch
  ├─ ai_languageModel ← Google Gemini Chat Model
  ├─ ai_tool ← Supabase vector search
  ├─ ai_outputParser ← Structured Output Parser
  └─ ai_memory ← Simple Memory

Switch
  ├─ Route 0 → Line Messaging QR
  │                └─ main → Store Visitor Log (end)
  ├─ Route 1 → Store Issue
  │                └─ main → Store Complaint Record
  │                              └─ main → Create Admin Notification
  │                                            └─ main → Complaint Reply (end)
  ├─ Route 2 → Line Messaging chat (end)
  ├─ Route 3 → (empty)
  └─ Route 4 → (empty)

Embeddings
  └─ ai_embedding → Supabase vector search, Supabase Vector Store

Upload your file here
  └─ main → Supabase Vector Store

Default Data Loader
  └─ ai_document → Supabase Vector Store
```

### Load Data Flow (Independent)
```
Upload your file here → Default Data Loader → Supabase Vector Store (insert)
                                                     ↑
                                              Embeddings
```

---

## Credentials Used

| Name | Type | Used By |
|------|------|---------|
| **Line Messaging account** | LINE Messaging | Line Messaging Trigger, Line Messaging QR, Line Messaging chat, Complaint Reply |
| **Google Gemini(PaLM) Api account** | Google API | Google Gemini Chat Model, Embeddings |
| **Supabase account 2** | Supabase API | Supabase Vector Store, Supabase vector search |
| **Supabase - Django DB** | Supabase API | Store Visitor Log, Store Issue, Store Complaint Record, Create Admin Notification |

---

## Database Tables (Supabase — Django Project)

### `visit_logs` (NEW)

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `BIGINT` | PK, Auto-generated |
| `visitor_name` | `VARCHAR(255)` | NOT NULL |
| `license_plate` | `VARCHAR(50)` | NOT NULL |
| `line_user_id` | `VARCHAR(255)` | Nullable |
| `house_number` | `VARCHAR(50)` | Nullable |
| `status` | `VARCHAR(50)` | NOT NULL, Default: `pending` |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, Default: NOW() |
| `updated_at` | `TIMESTAMPTZ` | Nullable |

### `issues_issue` (existing, modified)

| Column | Type | Notes |
|--------|------|-------|
| `id` | `BIGINT` | PK |
| `title` | `VARCHAR` | ← complaint_subject |
| `description` | `TEXT` | ← complaint_description |
| `location` | `VARCHAR` | ← complaint_location |
| `priority` | `VARCHAR` | ← complaint_priority (critical/high/medium/low) |
| `status` | `VARCHAR` | Default: `pending` |
| `created_date` | `TIMESTAMPTZ` | ← NOW() |
| `reporter_line_id` | `VARCHAR(255)` | **NEW** — LINE user ID of reporter |
| `reporter_id` | `BIGINT` | FK to `users_user` — **made nullable** to allow LINE-only reports |
| `analysis_json` | `JSONB` | `{"source":"line_chatbot"}` |

### `issues_complaint` (existing)

| Column | Type | Notes |
|--------|------|-------|
| `issue_ptr_id` | `BIGINT` | PK, FK → issues_issue.id |
| `category` | `VARCHAR` | Default: `general` |
| `evidence_image` | `VARCHAR` | Nullable |

### `notifications_notification` (existing)

| Column | Type | Notes |
|--------|------|-------|
| `id` | `BIGINT` | PK |
| `title` | `VARCHAR` | "New complaint: {subject}" |
| `message` | `TEXT` | "Priority: {p} - {description}" |
| `created_at` | `TIMESTAMPTZ` | ← NOW() |

---

## MCP Configuration

The workflow is available via the n8n MCP server (`opencode.json`):

```json
{
  "mcp": {
    "n8n": {
      "type": "local",
      "command": ["n8n-mcp-server"],
      "environment": {
        "N8N_API_URL": "http://localhost:1234/api/v1",
        "N8N_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
    }
  }
}
```

---

## Version History

| Date | Changes |
|------|---------|
| 2026-02-06 | Initial workflow created from RAG starter template |
| 2026-05-07 | Updated active version with improved prompts |
| 2026-05-13 | **Major update**: Added database storage for visitor logs, complaints, and admin notifications. Added priority classification to AI Agent. |

---

## Notes

- The AI Agent prompt is in **Thai** and the bot replies in Thai ending with "ครับ"
- Visitor registrations generate a QR code with visitor name + license plate via `api.qrserver.com`
- The RAG knowledge base uses documents stored in Supabase vector store (separate project from the Django DB)
- Each complaint execution creates one notification record
- The `reporter_line_id` column allows admin dashboard to identify the LINE user who reported, without needing a Django user account lookup
- Error handling: if a Supabase INSERT fails, downstream nodes in the chain will also fail. Consider adding "Continue on Fail" for production use
