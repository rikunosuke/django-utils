from django.db import models


class DBLog(models.Model):
    class Meta:
        get_latest_by = "id"

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    levelname = models.CharField(max_length=32)
    logname = models.CharField(max_length=32, db_index=True)
    category = models.CharField(max_length=128, db_index=True)
    message = models.TextField()

    def __str__(self):
        return f"DBLog#{self.id}"
