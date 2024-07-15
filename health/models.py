from django.db import models

class ChatHistory(models.Model):
    username = models.CharField(max_length=255, default='testing')
    user_query = models.TextField()
    bot_health_plans = models.JSONField()
    bot_disease_symptoms = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.timestamp}"
