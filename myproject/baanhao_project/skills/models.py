from django.db import models


class Skill(models.Model):
    """skills_skill — DDL."""

    class Meta:
        db_table = 'skills_skill'

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TechnicianSkill(models.Model):
    """skills_technician_skill — junction (replaces skill_set text)."""

    class Meta:
        db_table = 'skills_technician_skill'
        constraints = [
            models.UniqueConstraint(fields=['technician', 'skill'], name='uniq_technician_skill_pair'),
        ]

    technician = models.ForeignKey(
        'users.Technician',
        on_delete=models.CASCADE,
        related_name='technician_skill_links',
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='technician_skill_links')

    def __str__(self):
        return f'{self.technician_id}:{self.skill.name}'
