# BaanHao — Final Presentation

> CN332 Object-Oriented Analysis & Design
> เน้น Design Patterns ที่ใช้จริงในระบบ

||

## Slide 1 — Title

# BaanHao
### Smart Living Management System

CN332 OOA&D · Final Presentation

__

**Team**
- 6710615292 — athiphat sunsit (PM, Front-end, Back-end, QA)
- 6710615185 — ภูริช อัมพะวา (Front-end, Back-end)
- 6710545010 — นพัตธีรา เหลาเกิ้มหุ่ง (Front-end)
- 6710615144 — ปณิธาน ตันตื้อ (Front-end)
- 6710685014 — ธีภพ รัตนทรัพย์ศิริ (Back-end)

||

## Slide 2 — Problem Statement

### ปัญหาที่เจอ

__

**ฝั่งนิติบุคคล (Juristic)**
- workflow ซ้ำซาก ตอบคำถามเดิมๆ ทุกวัน
- รับเรื่องร้องเรียนกระจัดกระจาย ไม่มีระบบ track
- ไม่มี data รวมศูนย์เพื่อ analyze

**ฝั่งลูกบ้าน (Resident)**
- ติดต่อนิติฯ ยาก รอตอบนาน
- ไม่รู้จะส่งเรื่องร้องเรียนยังไง
- ผู้มาเยี่ยมเข้าหมู่บ้านยุ่งยาก

||

## Slide 3 — Solution Overview

### 2 Surfaces · 1 Database

__

```
   LINE OA  (Resident)         Web App  (Juristic)
        |                            |
        v                            v
    n8n + AI                    Django MTV
   (Gemini 2.5)              (8 Apps · ORM)
        |                            |
        +------------+---------------+
                     v
            Supabase Postgres
            (Shared State)
```

ลูกบ้านคุยกับ LINE OA → AI Agent route ตาม intent → เขียนลง DB ตัวเดียวกับ Django

||

## Slide 4 — Big Picture (End-to-End)

### Layered Architecture · 2 Paths

__

| Layer | LINE Side | Web Side |
|-------|-----------|----------|
| ① Client | LINE App | Browser |
| ② Channel | LINE Messaging API | HTTPS + gunicorn |
| ③ Orchestration | n8n workflow (22 nodes) | Django URL router + Middleware |
| ④ Logic/AI | Gemini 2.5 + RAG + Memory | Django Apps (MTV) |
| ⑤ Routing | Switch by intent | ORM + Storage |
| ⑥ **Persistence** | **Supabase Postgres (shared)** | |
| ⑦ Output | LINE reply / Flex QR | HTML response |

||

## Slide 5 — Tech Stack

### What we built with

__

**Backend** · Django 5.2 · Python · PostgreSQL (Supabase)
**LINE Integration** · n8n · LINE Messaging API · Gemini 2.5 Flash Lite
**Auth** · django-allauth (Google + LINE OAuth)
**Storage** · S3 (boto3 + django-storages)
**RAG** · Supabase Vector Store + Gemini Embeddings
**Tools** · Figma · Git · GitHub Projects (Kanban)

||

## Slide 6 — Design Patterns Map

### 14 GoF Patterns ใช้จริงในระบบ

__

| Category | Patterns |
|----------|----------|
| **Creational** | Singleton · Abstract Factory · Builder |
| **Structural** | Adapter · Facade · Composite · Decorator · Proxy |
| **Behavioral** | Strategy · Template Method · Chain of Responsibility · Command · Iterator · State |

วันนี้จะ **deep-dive 5 ตัว** ที่ impact สูงสุด · ที่เหลืออยู่ใน backup slides

||

## Slide 7 — Pattern 1 · Abstract Factory

### `users/models.py` — Role-based Architecture

__

**ปัญหา** — ระบบมี 5 role (Resident, Technician, JuristicOfficer, Security, Admin) แต่ละ role มี attributes ต่างกัน · ถ้าเอามารวมใน User class เดียวจะบวม

**Solution** — `User(AbstractUser)` เป็น abstract base · แต่ละ role เป็น concrete product แยก OneToOne

```python
class User(AbstractUser):
    role = models.CharField(choices=UserRole.choices)
    phone_number = models.CharField(...)
    line_id = models.CharField(...)

class Resident(models.Model):
    user = models.OneToOneField(User, related_name='resident_profile')
    house = models.ForeignKey('properties.House', ...)
    is_owner = models.BooleanField(default=False)

class Technician(models.Model):
    user = models.OneToOneField(User, related_name='technician_profile')
    skill_set = models.TextField()
    current_status = models.CharField(default="AVAILABLE")
```

__

**Why it matters** — เพิ่ม role ใหม่ได้โดยไม่กระทบ User · ตอบ feedback อาจารย์เรื่อง inheritance ที่ยืดหยุ่น

||

## Slide 8 — Pattern 2 · Adapter + Template Method

### `users/adapters.py` — `CustomSocialAccountAdapter`

__

**ปัญหา** — django-allauth login เสร็จเลย แต่เราต้องการ admin approval ก่อน + จัดการ email conflict

**Solution** — extend `DefaultSocialAccountAdapter` แล้ว override hooks (Template Method) เพื่อแปลง flow ให้เข้ากับ BaanHao (Adapter)

```python
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.is_active = False     # ต้องรอ admin อนุมัติ
        user.role = UserRole.RESIDENT
        user.save()
        raise ImmediateHttpResponse(redirect('users:social_extra_info'))

    def pre_social_login(self, request, sociallogin):
        if not sociallogin.user.is_active:
            messages.info(request, "Pending admin approval.")
            raise ImmediateHttpResponse(redirect('users:register'))
```

__

**Why it matters** — ไม่แก้ library ต้นทาง · ขยาย flow ของเราได้อิสระ · 2 patterns ใน class เดียว

||

## Slide 9 — Pattern 3 · Chain of Responsibility

### Django Middleware Stack

__

**ปัญหา** — request หนึ่งตัวต้องผ่าน security check, session, CSRF, auth, messages — ถ้าเขียนรวมใน view จะยุ่งและซ้ำ

**Solution** — แต่ละ middleware เป็น handler · request ผ่านไปตามลำดับ · handler ไหน reject ก็ short-circuit ได้เลย

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',          # ① HTTPS + headers
    'django.contrib.sessions.middleware.SessionMiddleware',   # ② load session
    'django.middleware.csrf.CsrfViewMiddleware',              # ③ validate CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',# ④ attach user
    'django.contrib.messages.middleware.MessageMiddleware',   # ⑤ flash msgs
    'allauth.account.middleware.AccountMiddleware',           # ⑥ allauth hooks
]
```

```
Request → ① → ② → ③ ─invalid─→ 403 Forbidden (short-circuit)
                  └─valid─→ ④ → ⑤ → ⑥ → View → Response
```

__

**Why it matters** — แต่ละ handler รับผิดชอบเรื่องเดียว · เพิ่ม/ลบ/สลับลำดับได้โดยไม่กระทบ logic อื่น

||

## Slide 10 — Pattern 4 · State

### `issues/models.py` — Issue Lifecycle

__

**ปัญหา** — Issue แต่ละใบมี lifecycle ชัดเจน (รอ → ดำเนินการ → จบ/เกินกำหนด) · ถ้าใช้ flag boolean หลายตัวจะ track ยาก

**Solution** — TextChoices กำหนด states · transition เกิดใน views

```python
class IssueStatus(models.TextChoices):
    PENDING     = 'PENDING',     'Pending'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    OVERDUE     = 'OVERDUE',     'Overdue'
    SUCCESS     = 'SUCCESS',     'Success'

# views.py — State transition
if action == 'complete':
    task.status = IssueStatus.SUCCESS   # IN_PROGRESS → SUCCESS
    task.save()
```

__

**State Diagram**

```
   [*] ──create──> PENDING
   PENDING ──assign technician──> IN_PROGRESS
   IN_PROGRESS ──complete──> SUCCESS ──> [*]
   IN_PROGRESS ──deadline passed──> OVERDUE
   OVERDUE ──reassign──> IN_PROGRESS
```

__

**Why it matters** — lifecycle เป็น explicit · valid transitions ควบคุมได้จากที่เดียว

||

## Slide 11 — Pattern 5 · Facade

### Django ORM + CLI Menu

__

**ปัญหา** — query ที่ต้อง JOIN หลายตาราง ถ้าเขียน raw SQL ทุกครั้งจะซ้ำซ้อนและ error ง่าย

**Solution 1 — ORM ซ่อน SQL**

```python
# โค้ดที่เราเขียน
tasks = Maintenance.objects.select_related(
    'issue_ptr', 'reporter', 'technician'
).order_by('-created_date')

# SQL ที่ Django generate เบื้องหลัง (เราไม่ต้องเขียน)
# SELECT m.*, i.*, r.*, t.* FROM issues_maintenance m
#   INNER JOIN issues_issue i ON ...
#   LEFT OUTER JOIN users_resident r ON ...
#   LEFT OUTER JOIN users_technician t ON ...
#   ORDER BY i.created_date DESC
```

**Solution 2 — `manage_tasks_menu()` ซ่อน CLI sub-operations**

```python
def manage_tasks_menu(tasks, user):     # Facade
    if choice == "1": view_all_tasks(tasks)
    elif choice == "3": add_task(tasks)
    elif choice == "4": update_task(tasks, user)
    elif choice == "5": delete_task(tasks, user)
```

__

**Why it matters** — client เรียก method เดียว · ความซับซ้อนซ่อนหลัง interface

||

## Slide 12 — Other 9 Patterns (Quick)

### ใช้จริงแต่ deep-dive ไม่ทัน

__

| Pattern | จุดที่ใช้ |
|---------|----------|
| **Singleton** | `settings.py` — Python module โหลดครั้งเดียว · ทุก app อ้างอิง config object เดียวกัน |
| **Builder** | `Issue.objects.all().filter().exclude().order_by()` — chain query ทีละขั้น |
| **Composite** | `base.html` + `{% block %}` · `urls.py` `include()` รวม sub-URLs |
| **Decorator** | `@login_required` บน view functions · stack ได้หลายชั้น |
| **Proxy** | Lazy QuerySet (รอ evaluate) + MTI `issue_ptr` (proxy ไปยัง parent table) |
| **Strategy** | `AUTHENTICATION_BACKENDS` — เลือก ModelBackend หรือ AllauthBackend |
| **Command** | CLI `view/search/add/update/delete_task()` — แต่ละ function = command อิสระ |
| **Iterator** | `Paginator` — traverse QuerySet เป็น page ๆ |

📎 รายละเอียดแต่ละตัวอยู่ใน `myproject/baanhao_project/ARCHITECTURE.md`

||

## Slide 13 — Class Diagram (Domain Model)

### User · Property · Issue Relationships

__

```
User (AbstractUser)
 ├──1:1── Resident ────FK──── House ───1:N─── Vehicle
 ├──1:1── Technician
 ├──1:1── JuristicOfficer
 ├──1:1── Security
 ├──1:1── Admin
 └──1:1── RegistrationRequest

Issue (Parent)
 ├── Complaint     (MTI: issue_ptr)
 └── Maintenance   (MTI: issue_ptr)──FK──> Technician

Issue.reporter ──FK──> Resident
```

__

**Key Design Decisions**
- **Multi-Table Inheritance** — `Complaint` / `Maintenance` extends `Issue` (รวม polymorphism + เก็บ field เฉพาะ)
- **Nullable reporter** — รองรับ LINE-only report (ไม่มี Django user)
- **`reporter_line_id` column** — track LINE user ที่ส่งเรื่องโดยไม่ต้องสร้าง User

||

## Slide 14 — LINE OA Capabilities

### AI Agent · 3 Intents

__

**1. ตอบกฎหมู่บ้าน** (intent = `general`)
```
ลูกบ้านถาม → AI Agent → RAG Retriever → Supabase Vector Store
                                        ↓
                                LINE reply (text)
```
ใช้ Gemini Embeddings + Vector Store เก็บกฎที่ upload ผ่านฟอร์ม

__

**2. Smart Ticket ผู้เยี่ยมชม** (intent = `visitor`)
```
"เพื่อนจะมาหา" → AI เก็บ ชื่อ + ทะเบียนรถ → INSERT visit_logs
                                          → LINE Flex Message + QR Code
```

__

**3. รับเรื่องร้องเรียน** (intent = `complaint`)
```
"ไฟทางเดินดับ" → AI เก็บหัวข้อ/สถานที่/รายละเอียด + จัด priority
              → INSERT issues_issue + issues_complaint + notification
              → นิติบุคคลเห็นใน Web Dashboard ทันที
```

||

## Slide 15 — Demo Screenshots

### ระบบจริง

__

**Web Dashboard** — overview, task summary, recent activity
**All Tasks Page** — search + filter + pagination (Builder + Iterator)
**Pending Registrations** — admin approval flow (State + Adapter)
**LINE OA Chat** — 3 intents in action
**QR Visitor Ticket** — Flex Message preview

🎥 GUI walkthrough · https://youtu.be/igLxI9eYJGI
📱 LINE OA demo · https://youtube.com/shorts/j89uEZ3Yu6c

||

## Slide 16 — Team & Progress

### Task Distribution

__

| Member | Total | ✅ Done | 🟢 In Progress | 🔵 Backlog |
|--------|:-----:|:------:|:--------------:|:----------:|
| @athiphat67 | 29 | 23 | 1 | 5 |
| @theepop66 | 24 | 18 | 1 | 5 |
| @6710615185 | 23 | 17 | 1 | 5 |
| @panifield | 16 | 10 | 1 | 5 |
| @napattiral276 | 15 | 9 | 1 | 5 |

**Methodology** — Agile · GitHub Projects (Kanban Board) · 12 Iterations
**Repo** — github.com/theepop66/CN332-group-project

||

## Slide 17 — Lessons Learned

### สิ่งที่ได้จากโปรเจกต์นี้

__

**1. Design Pattern ไม่ใช่ของแต่ง**
ทุก pattern ที่ใช้เกิดจากปัญหาจริง — ไม่ได้ใส่เพื่อให้ดูซับซ้อน

**2. Inheritance ที่ยืดหยุ่น (ตอบ feedback อาจารย์)**
แยก User (auth) ออกจาก Role profiles (business) ทำให้ extend role ใหม่ได้โดยไม่กระทบของเก่า

**3. Shared State ระหว่างทีม**
LINE side (n8n) + Web side (Django) ใช้ DB เดียวกัน → schema design ต้องคิดล่วงหน้า

**4. Future Work**
- Mobile native app
- Payment integration
- Notification push (LINE Push API)
- Multi-tenant (รองรับหลายโครงการ)

||

## Slide 18 — Q&A

# Thank You

__

**Repo** — github.com/theepop66/CN332-group-project
**Docs** — `BIG_PICTURE.md` · `ARCHITECTURE.md` · `SYSTEM_ARCHITECTURE.md`

📧 athiphatsunsit@gmail.com

||

## Backup Slides

> เผื่อโดนถามรายละเอียดเพิ่ม

||

## Backup 1 — Singleton (`settings.py`)

```python
# Python import system โหลด settings.py ครั้งเดียว
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', ...)
DATABASES = {'default': {...}}
INSTALLED_APPS = ['users', 'issues', ...]

# ทุกที่อ้างอิง object เดียวกัน
from django.conf import settings
print(settings.DEBUG)
```

||

## Backup 2 — Builder (QuerySet chaining)

```python
task_list = Issue.objects.all() \
    .select_related('reporter') \
    .order_by('-created_date')

if search_query:
    task_list = task_list.filter(
        Q(title__icontains=search_query) |
        Q(location__icontains=search_query)
    )

if status_filter == 'waiting':
    task_list = task_list.filter(status=IssueStatus.PENDING)

# Final result
paginator = Paginator(task_list, 30)
```

||

## Backup 3 — Composite (Template inheritance)

```html
<!-- base.html — Root component -->
<html><body>
    {% block sidebar %}{% endblock %}
    {% block content %}{% endblock %}
</body></html>
```

```html
<!-- all_tasks.html — Child component -->
{% extends "base.html" %}
{% block content %}
    {% for task in tasks %}<div>{{ task.title }}</div>{% endfor %}
{% endblock %}
```

```python
# urls.py — Composite routing
urlpatterns = [
    path('users/', include('users.urls')),
    path('issues/', include('issues.urls')),
]
```

||

## Backup 4 — Decorator (`@login_required`)

```python
@login_required
def pending_registrations_view(request):
    if request.user.role != UserRole.ADMIN:
        return redirect('dashboard')
    pending = RegistrationRequest.objects.filter(status=RequestStatus.PENDING)
    return render(request, 'users/pending_registrations.html', {...})

@login_required
def approve_registration_view(request, request_id):
    ...
```

||

## Backup 5 — Proxy (Lazy QuerySet + MTI)

```python
# Lazy — ยังไม่ยิง SQL
task_list = Issue.objects.all().select_related('reporter')

if search_query:
    task_list = task_list.filter(Q(title__icontains=search_query))

# SQL ยิงจริงที่บรรทัดนี้ เมื่อต้องการข้อมูล
paginator = Paginator(task_list, 30)
```

```python
# MTI — issue_ptr คือ proxy ไป parent table
class Complaint(Issue):
    category = models.CharField(...)
    evidence_image = models.ImageField(...)

# เข้าถึง Issue fields ผ่าน Complaint ได้
for c in Complaint.objects.all():
    print(c.title)      # ผ่าน issue_ptr
    print(c.category)   # Complaint field
```

||

## Backup 6 — Strategy (Authentication Backends)

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
# Django ลอง authenticate ตาม order นี้
```

||

## Backup 7 — Command + Iterator (CLI)

```python
# Command — แต่ละ function = independent operation
def view_all_tasks(tasks): ...
def add_task(tasks): ...
def update_task(tasks, user): ...

# Iterator — Paginator + QuerySet
paginator = Paginator(task_list, 30)
page_obj = paginator.get_page(page_number)
for task in page_obj:    # iterator protocol
    process(task)
```

||

## Backup 8 — Authentication Sequence

```
User → Browser: Click Login with Google
Browser → Django: GET /users/social-login-check/google/
Django → Browser: session social_action = login
Browser → Allauth: GET /accounts/google/login/
Allauth → Google: Redirect to OAuth
Google → Allauth: Callback with token
Allauth → Adapter: pre_social_login()
Adapter → DB: Check user exists + is_active
[New User Path]
  Allauth → Adapter: save_user()
  Adapter → DB: Save user (is_active=False)
  Adapter → Browser: Redirect /users/social-extra-info/
  User fills extra info → RegistrationRequest created
  → Pending Admin Approval
[Existing Active User Path]
  Adapter → Browser: Allow login → Dashboard
```

||

## Backup 9 — Database Schema (Summary)

```
users_user
  id · username · email · password
  role · phone_number · line_id · gender

users_resident       (1:1 user)  · house_id · is_owner
users_technician     (1:1 user)  · skill_set · current_status
users_juristic       (1:1 user)  · officer_id · department
users_security       (1:1 user)  · station_id · shift_time
users_admin          (1:1 user)
users_regrequest     (1:1 user)  · status · reviewed_by · reviewed_at

properties_house     id · house_number · owner_id
properties_vehicle   house_id · license_plate · brand · color

issues_issue         reporter_id · reporter_line_id · title
                     priority · status · location · analysis_json
issues_complaint     issue_ptr · category · evidence_image
issues_maintenance   issue_ptr · equipment_type · technician_id
                     appointment_date · before_image · after_image

notifications_notification  title · message · created_at
visit_logs           visitor_name · license_plate · line_user_id · status
```
