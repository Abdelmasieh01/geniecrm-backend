from django.db import models

class Stage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.IntegerField(unique=True)  # Helps to order stages in the Kanban view
    color = models.CharField(max_length=7, default="#000")

    def __str__(self):
        return self.name

class Lead(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # Link each lead to a stage (e.g. New, Contacted, etc.)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="leads")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
