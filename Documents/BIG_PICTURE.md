# BaanHao — Big Picture (End-to-End Layered)

> ภาพรวมระบบ BaanHao สำหรับการนำเสนอ — แสดง flow ตั้งแต่ user สัมผัสระบบจนถึง database
> ทั้ง 2 ทาง (LINE OA สำหรับลูกบ้าน + Web App สำหรับนิติบุคคล) ลงที่ Supabase ตัวเดียวกัน

---

## 🎯 One-Line Summary

ลูกบ้านคุยกับ **LINE OA** → ผ่าน **n8n + AI (Gemini 2.5 Flash Lite + RAG)** → เขียนข้อมูลลง **Supabase Postgres** ตัวเดียวกับที่ **Django Web (สำหรับนิติบุคคล)** ใช้

---

## 🗺️ Big Picture Diagram

```
==================================================================================
                        BAANHAO  —  END-TO-END  LAYERED
==================================================================================

      LINE  OA  PATH  (Resident)              WEB  PATH  (Juristic / Admin)

   ___________________________            ___________________________
  |                           |          |                           |
  |    ① RESIDENT             |          |    ① JURISTIC OFFICER     |
  |    (Mobile / LINE App)    |          |    (Desktop Browser)      |
  |___________________________|          |___________________________|
              |                                       |
              v                                       v
   ___________________________            ___________________________
  |                           |          |                           |
  |    ② LINE Messaging API   |          |    ② HTTPS / gunicorn     |
  |    (LINE Platform Cloud)  |          |                           |
  |___________________________|          |___________________________|
              |                                       |
              v                                       v
   ___________________________            ___________________________
  |                           |          |                           |
  |    ③ n8n WORKFLOW         |          |    ③ DJANGO ROUTER        |
  |    "lineOArag" · 22 nodes |          |    + Middleware Chain     |
  |    (LINE Trigger node)    |          |    (Security/CSRF/Auth)   |
  |___________________________|          |___________________________|
              |                                       |
              v                                       v
   ___________________________            ___________________________
  |                           |          |                           |
  |    ④ AI AGENT (LLM)       |          |    ④ DJANGO APPS  (MTV)   |
  |    Gemini 2.5 Flash Lite  |          |    users · issues ·       |
  |    + Memory (last 5 msgs) |          |    complaints · notif ·   |
  |    + Structured Output    |          |    analytics · dashboard  |
  |    + RAG Tool             |          |                           |
  |___________________________|          |___________________________|
              |                                       |
              v                                       v
   ___________________________            ___________________________
  |                           |          |                           |
  |    ⑤ SWITCH  (Router)     |          |    ⑤ ORM + Storage        |
  |    by intent →            |          |    Django ORM             |
  |     • visitor             |          |    boto3 / django-storages|
  |     • complaint           |          |                           |
  |     • general             |          |                           |
  |___________________________|          |___________________________|
              |                                       |
              +-------------------+-------------------+
                                  |
                                  v
                       ___________________________
                      |                           |
                      |  ⑥ SHARED PERSISTENCE     |
                      |  ┌─────────────────────┐  |
                      |  │ Supabase Postgres   │  |
                      |  │ (Django DB)         │  |
                      |  └─────────────────────┘  |
                      |  ┌─────────────────────┐  |
                      |  │ Supabase Vector     │  |
                      |  │ Store (RAG docs)    │  |
                      |  └─────────────────────┘  |
                      |  ┌─────────────────────┐  |
                      |  │ S3 (image uploads)  │  |
                      |  └─────────────────────┘  |
                      |___________________________|
                                  |
                                  v
                       ___________________________
                      |                           |
                      |    ⑦ OUTPUT BACK          |
                      |    → LINE reply / Flex QR |
                      |    → HTML response        |
                      |___________________________|

==================================================================================
```

---

## 📚 Layer Cheatsheet

| # | Layer | LINE Side (Resident) | Web Side (Juristic) |
|---|-------|----------------------|---------------------|
| ① | **Client** | LINE OA บนมือถือ | Web browser |
| ② | **Channel** | LINE Messaging API | HTTPS / gunicorn |
| ③ | **Orchestration** | n8n workflow `lineOArag` | Django URL router + middleware |
| ④ | **Logic / AI** | AI Agent (Gemini 2.5 Flash Lite) + RAG + Memory | Django Apps (Views + Forms) |
| ⑤ | **Routing / Access** | Switch by `intent` | ORM + Storage |
| ⑥ | **Persistence** | Supabase Postgres · Vector Store · S3 (shared) | |
| ⑦ | **Output** | LINE reply / Flex (QR) | HTML response |

---

## 🤖 LINE OA — 3 Capabilities (What it does today)

### 1️⃣  ตอบคำถามกฎหมู่บ้าน  (intent = `general`)

```
 ____________________      ____________________      ____________________
|                    |    |                    |    |                    |
|  Resident asks     |--->|   AI Agent calls   |--->|  Supabase Vector   |
|  "หมาเลี้ยงได้มั้ย"   |    |   RAG retriever    |    |  Store (rules)     |
|____________________|    |____________________|    |____________________|
                                    |
                                    v
                          ____________________
                         |                    |
                         |  LINE reply (text) |
                         |____________________|
```
- ใช้ **Supabase Vector Store** + **Gemini Embeddings** เก็บกฎระเบียบที่ upload ผ่านฟอร์ม
- AI Agent retrieve เอกสารที่ relevant แล้วตอบตามบริบท


### 2️⃣  ออก Smart Ticket สำหรับผู้เยี่ยมชม  (intent = `visitor`)

```
 ____________________      _____________________     _____________________
|                    |    |                     |   |                     |
|  Resident:         |--->|  AI collects:       |-->|  When complete:     |
|  "เพื่อนจะมาหา"      |    |   • ชื่อ-นามสกุล      |   |  is_ticket_ready    |
|____________________|    |   • ทะเบียนรถ        |   |       = true        |
                          |_____________________|   |_____________________|
                                                              |
              ___________________________________             |
             |                                   |            |
             v                                   v            v
   _____________________            __________________________
  |                     |          |                          |
  |  LINE Flex Message  |          |  INSERT visit_logs       |
  |  with QR (visitor + |          |  (visitor_name,          |
  |   license plate)    |          |   license_plate,         |
  |  via qrserver.com   |          |   line_user_id, status)  |
  |_____________________|          |__________________________|
```
- AI ไล่ถามจนได้ครบ 2 fields แล้วค่อย route
- QR ไป gen ที่ `api.qrserver.com` แล้วส่งเป็น Flex Message
- ข้อมูลเก็บใน table `visit_logs` (status = `pending` รอ ยาม/นิติ ยืนยัน)


### 3️⃣  รับเรื่องร้องเรียน  (intent = `complaint`)

```
 ____________________      _____________________     _____________________
|                    |    |                     |   |                     |
|  Resident:         |--->|  AI collects:       |-->|  When complete:     |
|  "ไฟทางเดินดับ"      |    |   • หัวข้อ            |   |  is_complaint_ready |
|____________________|    |   • สถานที่           |   |       = true        |
                          |   • รายละเอียด        |   |                     |
                          |   + AI จัด priority  |   |   priority:          |
                          |     (crit/high/      |   |   critical / high /  |
                          |      med/low)        |   |   medium / low       |
                          |_____________________|   |_____________________|
                                                              |
                ____________________________________________  |
               |                                            | |
               v                                            v v
   _____________________   _____________________   _____________________
  |                     | |                     | |                     |
  |  INSERT             | |  INSERT             | |  INSERT             |
  |  issues_issue       |>|  issues_complaint   |>|  notifications_     |
  |  (title, desc,      | |  (issue_ptr_id,     | |  notification       |
  |   location,         | |   category=         | |  (title, message,   |
  |   priority, status, | |   "general")        | |   for admin)        |
  |   reporter_line_id) | |                     | |                     |
  |_____________________| |_____________________| |_____________________|
                                                              |
                                                              v
                                                  _____________________
                                                 |                     |
                                                 |  LINE reply         |
                                                 |  (AI-generated      |
                                                 |   acknowledgement)  |
                                                 |_____________________|
```
- ใช้ **Multi-Table Inheritance** ของ Django: `issues_issue` (parent) → `issues_complaint` (child)
- `reporter_line_id` ทำให้ track ได้ว่าใครส่ง โดยไม่ต้องมี Django user
- `reporter_id` ใน `issues_issue` ทำ nullable เพื่อรองรับ LINE-only report
- นิติบุคคลเห็นใน Web Dashboard ผ่านหน้า All Tasks ทันที

---

## 🔌 Web Side — Juristic Officer

```
 ____________________      ____________________      ____________________
|                    |    |                    |    |                    |
|  Browser           |--->|  Django Middleware |--->|  URL Router        |
|  (login session)   |    |  Security/CSRF/    |    |  → apps/views      |
|                    |    |  Auth/Messages     |    |                    |
|____________________|    |____________________|    |____________________|
                                                              |
                                                              v
                                                    ____________________
                                                   |                    |
                                                   |  Views (MTV)       |
                                                   |  • all_tasks       |
                                                   |  • dashboard       |
                                                   |  • notifications   |
                                                   |  • analytics       |
                                                   |____________________|
                                                              |
                                                              v
                                                    ____________________
                                                   |                    |
                                                   |  ORM →             |
                                                   |  Supabase Postgres |
                                                   |____________________|
                                                              |
                                                              v
                                                    ____________________
                                                   |                    |
                                                   |  Template Engine   |
                                                   |  base.html +       |
                                                   |  child templates   |
                                                   |____________________|
                                                              |
                                                              v
                                                       HTML Response
```

---

## 🔄 Shared State — ทำไม 2 ฝั่งถึงสื่อสารกันได้

```
                  ┌───────────────────────────────────────┐
                  │     SAME  SUPABASE  POSTGRES          │
                  ├───────────────────────────────────────┤
                  │  • visit_logs                         │
                  │  • issues_issue + issues_complaint    │
                  │  • notifications_notification         │
                  │  • users_user / users_resident / ...  │
                  └───────────────────────────────────────┘
                          ▲                    ▲
                          │ writes             │ reads + writes
                          │                    │
                  ┌───────┴────────┐   ┌───────┴────────┐
                  │   n8n          │   │   Django       │
                  │   (LINE side)  │   │   (Web side)   │
                  └────────────────┘   └────────────────┘
```

- n8n เขียนเข้า table ที่ Django เป็นเจ้าของ schema → schema ต้องสอดคล้อง
- เพิ่ม column `reporter_line_id` ใน `issues_issue` เพื่อรองรับ report จาก LINE โดยไม่มี user
- Django Admin / Dashboard อ่านข้อมูลที่ n8n เขียนได้ทันที (real-time view)

---

## 🛠️ Technology Stack (per Layer)

| Layer | LINE Side | Web Side |
|-------|-----------|----------|
| Client | LINE App | HTML / CSS / JS |
| Channel | LINE Messaging API | HTTPS + gunicorn + whitenoise |
| Orchestration | n8n (Docker) | Django 5.2 + URL routing |
| AI / Logic | Gemini 2.5 Flash Lite, Gemini Embeddings, LangChain (n8n) | Python Views + Forms + django-allauth |
| Memory / State | n8n Simple Memory (window=5) | Django Session |
| Routing | n8n Switch by JSON intent | Django URL `include()` |
| Data Access | n8n Supabase node | Django ORM |
| File Storage | — | boto3 + django-storages → S3 |
| Persistence | Supabase Postgres + Vector Store | Supabase Postgres + S3 |

---

## 🔐 Credentials & Config (per Surface)

| Credential | Stored In | Used By |
|------------|-----------|---------|
| `LINE Messaging account` | n8n credentials | LINE Trigger, QR sender, Reply sender |
| `Google Gemini API` | n8n credentials | LLM + Embeddings |
| `Supabase account 2` | n8n credentials | Vector store (RAG docs) |
| `Supabase — Django DB` | n8n credentials | Insert visit/complaint/notification |
| `DJANGO_SECRET_KEY` | `.env` | Django session signing |
| `DB_*` (Supabase Postgres) | `.env` | Django ORM connection |
| `AWS_*` | `.env` | django-storages → S3 |
| Google / LINE OAuth | `.env` | django-allauth login |

> ⚠️ **2 Supabase project แยกกัน:** Vector Store project (สำหรับ RAG) ≠ Django DB project (สำหรับ business data)
> ⚠️ **LINE OAuth login** (django-allauth) ≠ **LINE Messaging API** (n8n) — เป็นคนละ channel ใน LINE Developer Console

---

## 🧭 Reading Order (สำหรับคนที่จะอ่านต่อ)

1. **This file** — Big Picture, สำหรับนำเสนอภาพรวม
2. [`myproject/baanhao_project/SYSTEM_ARCHITECTURE.md`](myproject/baanhao_project/SYSTEM_ARCHITECTURE.md) — Layered architecture (Mermaid) เจาะลึก Django side
3. [`myproject/baanhao_project/ARCHITECTURE.md`](myproject/baanhao_project/ARCHITECTURE.md) — Design patterns ที่ใช้จริงในโค้ด
4. [`n8n-LineOA/workflow_n8n.md`](n8n-LineOA/workflow_n8n.md) — Detail ทุก node ของ n8n workflow
5. [`myproject/baanhao_project/DDL.sql`](myproject/baanhao_project/DDL.sql) — DB schema
