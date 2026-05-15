# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountEmailaddress(models.Model):
    email = models.CharField(unique=True, max_length=254)
    verified = models.BooleanField()
    primary = models.BooleanField()
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailaddress'
        unique_together = (('user', 'email'), ('user', 'primary'),)


class AccountEmailconfirmation(models.Model):
    created = models.DateTimeField()
    sent = models.DateTimeField(blank=True, null=True)
    key = models.CharField(unique=True, max_length=64)
    email_address = models.ForeignKey(AccountEmailaddress, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'account_emailconfirmation'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoSite(models.Model):
    domain = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'django_site'


class EventsEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey('UsersAdmin', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'events_event'


class InvoicesInvoice(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice_id = models.CharField(unique=True, max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20)
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    resident = models.ForeignKey('UsersResident', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'invoices_invoice'


class InvoicesTransaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    transaction_id = models.CharField(unique=True, max_length=50)
    paid_date = models.DateField()
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    slip_image_url = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    invoice = models.OneToOneField(InvoicesInvoice, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'invoices_transaction'


class IssuesComplaint(models.Model):
    issue_ptr = models.OneToOneField('IssuesIssue', models.DO_NOTHING, primary_key=True)
    category = models.CharField(max_length=50)
    evidence_image = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'issues_complaint'


class IssuesIssue(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    created_date = models.DateTimeField()
    location = models.CharField(max_length=100)
    analysis_json = models.JSONField(blank=True, null=True)
    reporter = models.ForeignKey('UsersResident', models.DO_NOTHING, blank=True, null=True)
    reporter_line_id = models.CharField(max_length=255, blank=True, null=True)
    assigned_officer = models.ForeignKey('UsersJuristicofficer', models.DO_NOTHING, blank=True, null=True)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'issues_issue'


class IssuesMaintenance(models.Model):
    issue_ptr = models.OneToOneField(IssuesIssue, models.DO_NOTHING, primary_key=True)
    equipment_type = models.CharField(max_length=100)
    appointment_date = models.DateTimeField(blank=True, null=True)
    before_image = models.CharField(max_length=100, blank=True, null=True)
    after_image = models.CharField(max_length=100, blank=True, null=True)
    technician = models.ForeignKey('UsersTechnician', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'issues_maintenance'


class NotificationsNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField()
    user = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    issue = models.ForeignKey(IssuesIssue, models.DO_NOTHING, blank=True, null=True)
    notification_type = models.CharField(max_length=50)
    is_read = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'notifications_notification'


class PropertiesHouse(models.Model):
    id = models.BigAutoField(primary_key=True)
    house_id = models.CharField(unique=True, max_length=20)
    house_number = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'properties_house'


class PropertiesVehicle(models.Model):
    id = models.BigAutoField(primary_key=True)
    license_plate = models.CharField(max_length=20)
    brand = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    house = models.ForeignKey(PropertiesHouse, models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'properties_vehicle'


class RegulationsRegulation(models.Model):
    id = models.BigAutoField(primary_key=True)
    rule_id = models.CharField(unique=True, max_length=50)
    category = models.CharField(max_length=50)
    topic = models.CharField(max_length=200)
    content = models.TextField()
    keywords = models.CharField(max_length=500, blank=True, null=True)
    last_updated = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'regulations_regulation'


class SkillsSkill(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'skills_skill'


class SkillsTechnicianSkill(models.Model):
    id = models.BigAutoField(primary_key=True)
    skill = models.ForeignKey(SkillsSkill, models.DO_NOTHING)
    technician = models.ForeignKey('UsersTechnician', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'skills_technician_skill'
        unique_together = (('technician', 'skill'),)


class SocialaccountSocialaccount(models.Model):
    provider = models.CharField(max_length=200)
    uid = models.CharField(max_length=191)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    extra_data = models.JSONField()
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialaccount'
        unique_together = (('provider', 'uid'),)


class SocialaccountSocialapp(models.Model):
    provider = models.CharField(max_length=30)
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=191)
    secret = models.CharField(max_length=191)
    key = models.CharField(max_length=191)
    provider_id = models.CharField(max_length=200)
    settings = models.JSONField()

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp'


class SocialaccountSocialappSites(models.Model):
    id = models.BigAutoField(primary_key=True)
    socialapp = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING)
    site = models.ForeignKey(DjangoSite, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialapp_sites'
        unique_together = (('socialapp', 'site'),)


class SocialaccountSocialtoken(models.Model):
    token = models.TextField()
    token_secret = models.TextField()
    expires_at = models.DateTimeField(blank=True, null=True)
    account = models.ForeignKey(SocialaccountSocialaccount, models.DO_NOTHING)
    app = models.ForeignKey(SocialaccountSocialapp, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'socialaccount_socialtoken'
        unique_together = (('app', 'account'),)


class UsersAdmin(models.Model):
    id = models.BigAutoField(primary_key=True)
    permission_level = models.CharField(max_length=20)
    user = models.OneToOneField('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_admin'


class UsersJuristicofficer(models.Model):
    id = models.BigAutoField(primary_key=True)
    officer_id = models.CharField(unique=True, max_length=20)
    department = models.CharField(max_length=100)
    user = models.OneToOneField('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_juristicofficer'


class UsersRegistrationrequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey('UsersUser', models.DO_NOTHING, blank=True, null=True)
    user = models.OneToOneField('UsersUser', models.DO_NOTHING, related_name='usersregistrationrequest_user_set')

    class Meta:
        managed = False
        db_table = 'users_registrationrequest'


class UsersResident(models.Model):
    id = models.BigAutoField(primary_key=True)
    is_owner = models.BooleanField()
    user = models.OneToOneField('UsersUser', models.DO_NOTHING)
    house = models.ForeignKey(PropertiesHouse, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_resident'


class UsersSecurity(models.Model):
    id = models.BigAutoField(primary_key=True)
    station_id = models.CharField(max_length=50)
    shift_time = models.CharField(max_length=50)
    user = models.OneToOneField('UsersUser', models.DO_NOTHING)
    is_on_duty = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'users_security'


class UsersTechnician(models.Model):
    id = models.BigAutoField(primary_key=True)
    current_status = models.CharField(max_length=20)
    user = models.OneToOneField('UsersUser', models.DO_NOTHING)
    current_maintenance = models.ForeignKey(IssuesMaintenance, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_technician'


class UsersUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    line_id = models.CharField(unique=True, max_length=50, blank=True, null=True)
    phone_number = models.CharField(unique=True, max_length=15, blank=True, null=True)
    profile_image = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_user'


class UsersUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_groups'
        unique_together = (('user', 'group'),)


class UsersUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_user_permissions'
        unique_together = (('user', 'permission'),)


class VisitLogs(models.Model):
    id = models.BigAutoField(primary_key=True)
    visitor_name = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=50)
    line_user_id = models.CharField(max_length=255, blank=True, null=True)
    house_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'visit_logs'


class VisitorsVisitorpass(models.Model):
    id = models.BigAutoField(primary_key=True)
    pass_id = models.CharField(unique=True, max_length=50)
    visitor_name = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20, blank=True, null=True)
    schedule_date = models.DateTimeField()
    qr_code_string = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20)
    entry_time = models.DateTimeField(blank=True, null=True)
    exit_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.ForeignKey(UsersResident, models.DO_NOTHING)
    house = models.ForeignKey(PropertiesHouse, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'visitors_visitorpass'
