from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skills_skill'

class TechnicianSkill(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    technician = models.ForeignKey('users.Technician', on_delete=models.CASCADE)

    class Meta:
        db_table = 'skills_technician_skill'
