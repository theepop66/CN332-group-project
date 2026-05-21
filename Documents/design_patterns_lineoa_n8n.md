# Design Patterns — BaanHao LINE OA with n8n

ระบบ LINE OA ของ BaanHao ใช้ n8n เป็น Automation Workflow Engine เชื่อมต่อ LINE Messaging API, Google Gemini AI, และ Supabase Database

---

## Creational Patterns

### Builder

AI Agent สร้าง Structured Object ทีละ field ผ่านการสนทนาหลายรอบ จนกว่าจะครบก่อน execute

```
ลูกบ้าน: "มีคนมาหา"
  → Bot: "ชื่อ-นามสกุล?"
ลูกบ้าน: "สมชาย ใจดี"
  → Bot: "ทะเบียนรถ?"
ลูกบ้าน: "กข 1234"
  → is_ticket_ready = true  ← Object สมบูรณ์
  → ออก Smart Ticket QR
```

**Structured Output ที่ถูก Build ทีละ field:**
```json
{
  "intent": "visitor",
  "is_ticket_ready": true,
  "visitor_name": "สมชาย ใจดี",
  "license_plate": "กข 1234",
  "reply": "..."
}
```

> AI Agent ไม่ trigger action จนกว่า Object จะครบสมบูรณ์ — เป็นแนวคิดเดียวกับ Builder Pattern

---

## Structural Patterns

### Adapter

n8n Node แต่ละตัวทำหน้าที่ **Adapt** API ที่แตกต่างกันให้คุยกันได้ภายใน Workflow เดียว

```
LINE Messaging API   ──►  lineMessagingTrigger  ──►  [n8n internal format]
Google Gemini API    ──►  lmChatGoogleGemini    ──►  [n8n internal format]
Supabase REST API    ──►  supabaseNode          ──►  [n8n internal format]
```

- แต่ละ Node แปลง interface ของ external service ให้เป็น format เดียวกัน
- Workflow ไม่ต้องรู้รายละเอียดของแต่ละ API โดยตรง

---

### Facade

n8n Workflow ทำหน้าที่เป็น **Single Entry Point** ซ่อนความซับซ้อนทั้งหมดจากลูกบ้าน

```
ลูกบ้าน (LINE)
      │
      ▼
┌─────────────────────────────────────────┐
│           n8n Workflow (Facade)          │
│                                         │
│  LINE API · Gemini AI · Supabase DB     │
│  Vector Search · Notification System   │
└─────────────────────────────────────────┘
```

- ลูกบ้านเห็นแค่ "chat กับ LINE" แต่ด้านหลังมี 4 services ทำงานร่วมกัน
- ถ้าเปลี่ยน AI Model หรือ Database ลูกบ้านไม่รู้สึกว่ามีการเปลี่ยนแปลง

---

## Behavioral Patterns

### Strategy

Switch Node เลือก **Strategy** การจัดการที่ต่างกัน 3 แบบตาม Intent ที่ AI จำแนก

```
                   AI Agent
                  (Intent Classification)
                        │
                     Switch
              ┌─────────┼──────────┐
              ▼         ▼          ▼
         "visitor"  "complaint"  "general"
              │         │          │
         [Strategy 1] [Strategy 2] [Strategy 3]
         QR Ticket    4-node       RAG
         + Log DB     pipeline     Answer
```

| Route | Condition | Strategy |
|---|---|---|
| 0 | `is_ticket_ready = true` | ออก QR + บันทึก visit_logs |
| 1 | `is_complaint_ready = true` | บันทึก + แจ้ง Admin |
| 2 | `intent = "general"` | ค้น Vector Store + ตอบ |

> เพิ่ม Intent ใหม่ได้โดยเพิ่ม Route ใน Switch โดยไม่แก้ Logic เดิม

---

### Template Method

AI Agent Prompt กำหนด **Template Algorithm** คงที่ แต่ขั้นตอนย่อย (Intent handling) ต่างกันตาม Intent

```
Template (คงที่สำหรับทุกข้อความ):
  Step 1: จำแนก Intent  →  visitor | complaint | general
  Step 2: ตรวจสอบข้อมูลครบ  →  ถามเพิ่มถ้าไม่ครบ
  Step 3: กำหนด Priority  →  critical | high | medium | low
  Step 4: สร้าง Reply  →  ตอบกลับลูกบ้าน

[ขั้นตอนย่อยต่างกัน]
  visitor   → ตรวจ visitor_name + license_plate
  complaint → ตรวจ subject + location + description
  general   → ค้น Vector Store
```

> Structure การทำงานเหมือนกันทุก request แต่รายละเอียดแต่ละ Intent ต่างกัน

---

### Chain of Responsibility

การจัดการ Complaint ส่งต่อข้อมูลผ่าน Node เป็นทอดๆ แต่ละ Node มีหน้าที่เฉพาะ

```
[Complaint ครบ]
      │
      ▼
Store Issue               (1) บันทึก issues_issue
      │
      ▼
Store Complaint Record    (2) บันทึก issues_complaint
      │
      ▼
Create Admin Notification (3) สร้าง notifications_notification
      │
      ▼
Complaint Reply           (4) ส่ง LINE ยืนยันกลับลูกบ้าน
```

> แต่ละ Node รับผิดชอบ 1 งาน ถ้าต้องการเพิ่ม/ลบขั้นตอน แก้เฉพาะจุดนั้น

---

### State

สถานะของ Issue และ Visitor Log เปลี่ยนแปลงตาม lifecycle การจัดการปัญหา

```
Complaint:
  pending ──► in_progress ──► resolved

Visitor Log:
  pending ──► approved / rejected
```

- n8n สร้าง record ด้วย `status = "pending"` ทุกครั้ง
- Admin Dashboard (Django) อัปเดต State ตามการดำเนินการ
- พฤติกรรมระบบต่างกันตาม State (เช่น ไม่แจ้งเตือนซ้ำถ้า `in_progress`)

---

## สรุป

| Category | Pattern | ปรากฏใน System |
|---|---|---|
| **Creational** | Builder | AI Agent สะสม field จนครบแล้วค่อย trigger |
| **Structural** | Adapter | n8n Nodes แปลง API ต่างๆ ให้ใช้งานร่วมกันได้ |
| **Structural** | Facade | n8n เป็น Single Entry Point ซ่อน complexity |
| **Behavioral** | Strategy | Switch + 3 Intent Routes |
| **Behavioral** | Template Method | AI Prompt เป็น Template สำหรับทุก request |
| **Behavioral** | Chain of Responsibility | Complaint pipeline 4 nodes |
| **Behavioral** | State | Issue/Visitor status lifecycle |

---

## Architecture รวม

```
LINE OA
   │ Webhook
   ▼
n8n Workflow (Facade + Adapter)
   │
   ▼
AI Agent ──── Template Method (จำแนก Intent)
   │                │ Builder (สะสม field)
   ▼
Switch ──────────── Strategy (เลือก Route)
   │
   ├── visitor  → QR + DB
   ├── complaint → Chain of Responsibility (4 nodes) + State (pending)
   └── general  → RAG (Supabase Vector + Gemini)
```

> **Stack:** n8n · Google Gemini 2.5 Flash Lite · Supabase (PostgreSQL + pgvector) · LINE Messaging API · Docker
