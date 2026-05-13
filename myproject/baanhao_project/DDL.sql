-- =============================================================
--  BaanHao Database Schema (Corrected)
--  Engine  : PostgreSQL 15+
--  Note    : ใช้ PostgreSQL แทน SQLite3 สำหรับ production
--            เปลี่ยน settings.py → ENGINE = 'django.db.backends.postgresql'
-- =============================================================

-- -------------------------------------------------------------
--  EXTENSIONS
-- -------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()


-- =============================================================
--  DJANGO BUILT-IN TABLES  (Django จัดการเอง ไม่ต้องสร้างเอง)
--  auth_group, auth_permission, auth_group_permissions,
--  django_content_type, django_migrations, django_session,
--  django_site, django_admin_log
-- =============================================================


-- =============================================================
--  1. USERS  —  Base + Subtypes (Table-Per-Subtype Inheritance)
-- =============================================================

-- 1.1 Base user (extends AbstractUser ของ Django)
CREATE TABLE users_user (
    id              BIGSERIAL       PRIMARY KEY,
    -- Django AbstractUser fields
    password        VARCHAR(128)    NOT NULL,
    last_login      TIMESTAMP       NULL,
    is_superuser    BOOLEAN         NOT NULL DEFAULT FALSE,
    username        VARCHAR(150)    NOT NULL UNIQUE,
    first_name      VARCHAR(150)    NOT NULL DEFAULT '',
    last_name       VARCHAR(150)    NOT NULL DEFAULT '',
    email           VARCHAR(254)    NOT NULL UNIQUE,
    is_staff        BOOLEAN         NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    date_joined     TIMESTAMP       NOT NULL DEFAULT NOW(),
    -- Custom fields
    line_id         VARCHAR(50)     NULL UNIQUE,
    phone_number    VARCHAR(15)     NULL UNIQUE,
    profile_image   VARCHAR(255)    NULL,
    role            VARCHAR(20)     NOT NULL
                        CHECK (role IN ('admin','resident','technician',
                                        'security','juristic_officer')),
    gender          VARCHAR(10)     NULL
                        CHECK (gender IN ('male','female','other')),
    -- FIX: เพิ่ม updated_at ที่หายไปจาก schema เดิม
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_user_role  ON users_user (role);
CREATE INDEX idx_users_user_email ON users_user (email);


-- 1.2 Admin subtype
CREATE TABLE users_admin (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         BIGINT          NOT NULL UNIQUE
                        REFERENCES users_user (id) ON DELETE CASCADE,
    permission_level VARCHAR(20)    NOT NULL DEFAULT 'basic'
                        CHECK (permission_level IN ('basic','super')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- 1.3 Juristic Officer subtype
CREATE TABLE users_juristicofficer (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         BIGINT          NOT NULL UNIQUE
                        REFERENCES users_user (id) ON DELETE CASCADE,
    officer_id      VARCHAR(20)     NOT NULL UNIQUE,
    department      VARCHAR(100)    NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- 1.4 Technician subtype
--     FIX: ลบ skill_set TEXT ออก → ใช้ junction table แทน
--     FIX: เพิ่ม current_maintenance_id (FK เพิ่มทีหลังหลัง issues_maintenance พร้อม)
CREATE TABLE users_technician (
    id                      BIGSERIAL   PRIMARY KEY,
    user_id                 BIGINT      NOT NULL UNIQUE
                                REFERENCES users_user (id) ON DELETE CASCADE,
    current_status          VARCHAR(20) NOT NULL DEFAULT 'available'
                                CHECK (current_status IN ('available','busy','off_duty')),
    -- current_maintenance_id: FK จะ ADD CONSTRAINT ภายหลัง (หลีกเลี่ยง circular DDL)
    current_maintenance_id  BIGINT      NULL,
    created_at              TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP   NOT NULL DEFAULT NOW()
);


-- 1.5 Security subtype
CREATE TABLE users_security (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         BIGINT          NOT NULL UNIQUE
                        REFERENCES users_user (id) ON DELETE CASCADE,
    station_id      VARCHAR(50)     NOT NULL,
    shift_time      VARCHAR(50)     NOT NULL,
    is_on_duty      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- =============================================================
--  2. SKILLS  —  แยกตาราง + Junction (แทน skill_set TEXT)
-- =============================================================

CREATE TABLE skills_skill (
    id          SERIAL          PRIMARY KEY,
    name        VARCHAR(100)    NOT NULL UNIQUE,
    created_at  TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- FIX: Junction table แทน List<String>
CREATE TABLE skills_technician_skill (
    id              BIGSERIAL   PRIMARY KEY,
    technician_id   BIGINT      NOT NULL
                        REFERENCES users_technician (id) ON DELETE CASCADE,
    skill_id        INT         NOT NULL
                        REFERENCES skills_skill (id) ON DELETE CASCADE,
    UNIQUE (technician_id, skill_id)
);

CREATE INDEX idx_tech_skill_technician ON skills_technician_skill (technician_id);
CREATE INDEX idx_tech_skill_skill      ON skills_technician_skill (skill_id);


-- =============================================================
--  3. PROPERTIES
-- =============================================================

-- 3.1 House
--     FIX: ลบ owner_id FK ออก → หาเจ้าของด้วย
--          Resident.objects.get(house=house, is_owner=True)
--          เพื่อตัด circular FK กับ users_resident
CREATE TABLE properties_house (
    id              BIGSERIAL       PRIMARY KEY,
    house_id        VARCHAR(20)     NOT NULL UNIQUE,
    house_number    VARCHAR(20)     NOT NULL,
    -- FIX: เพิ่ม audit fields ที่หายไป
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- 3.2 Resident subtype
--     วางไว้หลัง properties_house เพื่อให้ FK ถูกต้อง
CREATE TABLE users_resident (
    id              BIGSERIAL   PRIMARY KEY,
    user_id         BIGINT      NOT NULL UNIQUE
                        REFERENCES users_user (id) ON DELETE CASCADE,
    house_id        BIGINT      NULL
                        REFERENCES properties_house (id) ON DELETE SET NULL,
    is_owner        BOOLEAN     NOT NULL DEFAULT FALSE,
    -- FIX: เพิ่ม audit fields
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_resident_house ON users_resident (house_id);


-- 3.3 Vehicle  (FIX: แยกตารางแทน registeredVehicles: List<String>  ← ทำไว้แล้ว ✓)
CREATE TABLE properties_vehicle (
    id              BIGSERIAL       PRIMARY KEY,
    house_id        BIGINT          NOT NULL
                        REFERENCES properties_house (id) ON DELETE CASCADE,
    license_plate   VARCHAR(20)     NOT NULL,
    brand           VARCHAR(50)     NULL,
    color           VARCHAR(30)     NULL,
    -- FIX: เพิ่ม audit fields
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vehicle_house         ON properties_vehicle (house_id);
-- FIX: เพิ่ม index license_plate สำหรับ Security scan
CREATE INDEX idx_vehicle_license_plate ON properties_vehicle (license_plate);


-- =============================================================
--  4. ISSUES  —  Base + Subtypes
-- =============================================================

-- 4.1 Base Issue
--     FIX: เพิ่ม assigned_officer_id ที่หายไป
--     FIX: analysis_json → JSONB (queryable) แทน TEXT+JSON_VALID
CREATE TABLE issues_issue (
    id                  BIGSERIAL       PRIMARY KEY,
    reporter_id         BIGINT          NOT NULL
                            REFERENCES users_resident (id) ON DELETE RESTRICT,
    -- FIX: เพิ่ม FK นี้ที่ขาดหายใน schema เดิม
    assigned_officer_id BIGINT          NULL
                            REFERENCES users_juristicofficer (id) ON DELETE SET NULL,
    title               VARCHAR(200)    NOT NULL,
    description         TEXT            NOT NULL,
    priority            VARCHAR(20)     NOT NULL DEFAULT 'medium'
                            CHECK (priority IN ('low','medium','high','urgent')),
    status              VARCHAR(20)     NOT NULL DEFAULT 'open'
                            CHECK (status IN ('open','in_progress','resolved','closed')),
    location            VARCHAR(100)    NOT NULL,
    -- FIX: JSONB แทน TEXT ใน PostgreSQL → สามารถ query ข้างใน JSON ได้
    analysis_json       JSONB           NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_issue_status          ON issues_issue (status);
CREATE INDEX idx_issue_reporter        ON issues_issue (reporter_id);
CREATE INDEX idx_issue_officer         ON issues_issue (assigned_officer_id);
-- FIX: index สำหรับ filter JSON field
CREATE INDEX idx_issue_analysis        ON issues_issue USING GIN (analysis_json);


-- 4.2 Maintenance subtype
CREATE TABLE issues_maintenance (
    issue_ptr_id        BIGINT          PRIMARY KEY
                            REFERENCES issues_issue (id) ON DELETE CASCADE,
    equipment_type      VARCHAR(100)    NOT NULL,
    technician_id       BIGINT          NULL
                            REFERENCES users_technician (id) ON DELETE SET NULL,
    appointment_date    TIMESTAMP       NULL,
    -- FIX: ชื่อ attribute ที่ถูกต้อง (ไม่ใช่ method)
    before_image_url    VARCHAR(255)    NULL,
    after_image_url     VARCHAR(255)    NULL,
    updated_at          TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_maintenance_technician ON issues_maintenance (technician_id);

-- FIX: เพิ่ม FK current_maintenance_id หลังจาก issues_maintenance พร้อมแล้ว
ALTER TABLE users_technician
    ADD CONSTRAINT fk_technician_current_maintenance
    FOREIGN KEY (current_maintenance_id)
    REFERENCES issues_maintenance (issue_ptr_id)
    ON DELETE SET NULL;

CREATE INDEX idx_technician_maintenance ON users_technician (current_maintenance_id);


-- 4.3 Complaint subtype
CREATE TABLE issues_complaint (
    issue_ptr_id    BIGINT          PRIMARY KEY
                        REFERENCES issues_issue (id) ON DELETE CASCADE,
    category        VARCHAR(50)     NOT NULL
                        CHECK (category IN ('noise','cleanliness','safety',
                                            'parking','neighbor','other')),
    evidence_image  VARCHAR(255)    NULL,
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- =============================================================
--  5. NOTIFICATIONS
--     FIX: เพิ่ม user_id, type, is_read, issue_id ที่หายไปทั้งหมด
-- =============================================================

CREATE TABLE notifications_notification (
    id          BIGSERIAL       PRIMARY KEY,
    user_id     BIGINT          NOT NULL
                    REFERENCES users_user (id) ON DELETE CASCADE,
    -- อ้างอิง issue ถ้า notification นี้มาจาก issue (optional)
    issue_id    BIGINT          NULL
                    REFERENCES issues_issue (id) ON DELETE SET NULL,
    type        VARCHAR(50)     NOT NULL
                    CHECK (type IN ('issue_update','announcement',
                                    'payment','visitor','event','system')),
    title       VARCHAR(255)    NOT NULL,
    message     TEXT            NOT NULL,
    is_read     BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notification_user    ON notifications_notification (user_id);
CREATE INDEX idx_notification_is_read ON notifications_notification (user_id, is_read);


-- =============================================================
--  6. EVENTS  (FIX: ตารางใหม่ที่ขาดหายจาก schema เดิม)
-- =============================================================

CREATE TABLE events_event (
    id              BIGSERIAL       PRIMARY KEY,
    created_by_id   BIGINT          NOT NULL
                        REFERENCES users_admin (id) ON DELETE RESTRICT,
    title           VARCHAR(200)    NOT NULL,
    description     TEXT            NOT NULL,
    event_date      TIMESTAMP       NOT NULL,
    location        VARCHAR(100)    NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_event_date ON events_event (event_date);


-- =============================================================
--  7. REGULATIONS  (FIX: ตารางใหม่ที่ขาดหายจาก schema เดิม)
-- =============================================================

CREATE TABLE regulations_regulation (
    id              BIGSERIAL       PRIMARY KEY,
    rule_id         VARCHAR(50)     NOT NULL UNIQUE,
    category        VARCHAR(50)     NOT NULL,
    topic           VARCHAR(200)    NOT NULL,
    content         TEXT            NOT NULL,
    keywords        VARCHAR(500)    NULL,
    last_updated    TIMESTAMP       NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- FIX: Full-text search index สำหรับ AI keyword matching
CREATE INDEX idx_regulation_fts ON regulations_regulation
    USING GIN (to_tsvector('english', topic || ' ' || COALESCE(keywords, '')));


-- =============================================================
--  8. INVOICES & TRANSACTIONS  (FIX: ตารางใหม่ที่ขาดหายทั้งคู่)
-- =============================================================

-- 8.1 Invoice
CREATE TABLE invoices_invoice (
    id              BIGSERIAL           PRIMARY KEY,
    invoice_id      VARCHAR(50)         NOT NULL UNIQUE,
    resident_id     BIGINT              NOT NULL
                        REFERENCES users_resident (id) ON DELETE RESTRICT,
    amount          NUMERIC(10, 2)      NOT NULL CHECK (amount >= 0),
    due_date        DATE                NOT NULL,
    status          VARCHAR(20)         NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','paid','overdue','cancelled')),
    type            VARCHAR(50)         NOT NULL
                        CHECK (type IN ('monthly_fee','utility','penalty','other')),
    created_at      TIMESTAMP           NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP           NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invoice_resident ON invoices_invoice (resident_id);
CREATE INDEX idx_invoice_status   ON invoices_invoice (status);
CREATE INDEX idx_invoice_due_date ON invoices_invoice (due_date);


-- 8.2 Transaction  (1 Invoice : 1 Transaction)
CREATE TABLE invoices_transaction (
    id                  BIGSERIAL       PRIMARY KEY,
    transaction_id      VARCHAR(50)     NOT NULL UNIQUE,
    invoice_id          BIGINT          NOT NULL UNIQUE
                            REFERENCES invoices_invoice (id) ON DELETE RESTRICT,
    paid_date           DATE            NOT NULL,
    paid_amount         NUMERIC(10, 2)  NOT NULL CHECK (paid_amount >= 0),
    slip_image_url      VARCHAR(255)    NULL,
    payment_status      VARCHAR(20)     NOT NULL DEFAULT 'pending'
                            CHECK (payment_status IN ('pending','verified','rejected')),
    created_at          TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP       NOT NULL DEFAULT NOW()
);


-- =============================================================
--  9. VISITOR PASSES  (FIX: ตารางใหม่ + เพิ่ม created_by_id)
-- =============================================================

CREATE TABLE visitors_visitorpass (
    id              BIGSERIAL       PRIMARY KEY,
    pass_id         VARCHAR(50)     NOT NULL UNIQUE
                        DEFAULT 'VP-' || UPPER(gen_random_uuid()::TEXT),
    house_id        BIGINT          NOT NULL
                        REFERENCES properties_house (id) ON DELETE CASCADE,
    -- FIX: FK กลับไปหา Resident ผู้สร้าง pass ที่หายไปใน schema เดิม
    created_by_id   BIGINT          NOT NULL
                        REFERENCES users_resident (id) ON DELETE RESTRICT,
    visitor_name    VARCHAR(100)    NOT NULL,
    license_plate   VARCHAR(20)     NULL,
    -- FIX: แก้ sheduleDate → schedule_date
    schedule_date   TIMESTAMP       NOT NULL,
    qr_code_string  VARCHAR(500)    NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','active','expired','cancelled')),
    entry_time      TIMESTAMP       NULL,
    exit_time       TIMESTAMP       NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_visitor_house         ON visitors_visitorpass (house_id);
CREATE INDEX idx_visitor_status        ON visitors_visitorpass (status);
CREATE INDEX idx_visitor_schedule      ON visitors_visitorpass (schedule_date);
-- FIX: index license_plate สำหรับ Security scan ที่ gate
CREATE INDEX idx_visitor_license_plate ON visitors_visitorpass (license_plate);


-- =============================================================
--  10. REGISTRATION REQUESTS  (มีอยู่แล้ว ✓ — เพิ่ม audit fields)
-- =============================================================

CREATE TABLE users_registrationrequest (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         BIGINT          NOT NULL UNIQUE
                        REFERENCES users_user (id) ON DELETE CASCADE,
    reviewed_by_id  BIGINT          NULL
                        REFERENCES users_user (id) ON DELETE SET NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','approved','rejected')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    reviewed_at     TIMESTAMP       NULL
);

CREATE INDEX idx_reg_request_status ON users_registrationrequest (status);


-- =============================================================
--  11. DJANGO-ALLAUTH  (Django/allauth จัดการ migration เอง)
--  account_emailaddress, account_emailconfirmation,
--  socialaccount_socialapp, socialaccount_socialaccount,
--  socialaccount_socialtoken, socialaccount_socialapp_sites
-- =============================================================


-- =============================================================
--  TRIGGER: auto-update updated_at
-- =============================================================

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- สร้าง trigger สำหรับทุก table ที่มี updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'users_user','users_admin','users_juristicofficer',
        'users_technician','users_security','users_resident',
        'properties_house','properties_vehicle',
        'issues_issue','issues_maintenance','issues_complaint',
        'events_event','invoices_invoice','invoices_transaction',
        'visitors_visitorpass'
    ] LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%s_updated_at
             BEFORE UPDATE ON %s
             FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();',
            t, t
        );
    END LOOP;
END;
$$;


-- =============================================================
--  SUMMARY OF FIXES APPLIED
-- =============================================================
--
--  [CRITICAL]
--  ✅ 1. Inheritance: ใช้ Table-Per-Subtype (user_id FK) ไม่มี MANY MANY แล้ว
--  ✅ 2. ลบ skill_set TEXT → skills_skill + skills_technician_skill junction table
--  ✅ 3. Object reference → FK integers ทุก table
--  ✅ 4. เพิ่ม assigned_officer_id FK ใน issues_issue
--
--  [MODERATE]
--  ✅ 5. ลบ owner_id ออกจาก properties_house (ตัด circular FK)
--  ✅ 6. analysis_json → JSONB พร้อม GIN index
--  ✅ 7. before/afterWorkImage() → before/after_image_url VARCHAR
--  ✅ 8. เพิ่ม current_maintenance_id กลับเข้า users_technician (ADD CONSTRAINT หลัง DDL)
--
--  [MINOR]
--  ✅ 9.  sheduleDate → schedule_date
--  ✅ 10. currentMaintananceID → current_maintenance_id
--  ✅ 11. tiltle → title
--  ✅ 12. เพิ่ม created_at/updated_at ทุก table + auto-update trigger
--  ✅ 13. เพิ่ม index: email, license_plate, status fields ทุก table
--  ✅ 14. เพิ่ม created_by_id FK ใน visitors_visitorpass
--
--  [NEW TABLES]
--  ✅ 15. events_event
--  ✅ 16. regulations_regulation (พร้อม full-text search index)
--  ✅ 17. invoices_invoice
--  ✅ 18. invoices_transaction
--  ✅ 19. visitors_visitorpass
--  ✅ 20. skills_skill + skills_technician_skill
--
--  [NOTIFICATION FIX]
--  ✅ 21. เพิ่ม user_id, issue_id, type, title, is_read ที่หายไปทั้งหมด