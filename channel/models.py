from pyexpat import model
from django.db import models

# Create your models here.
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    online = models.ManyToManyField(to=User, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_room")

    def get_online_count(self):
        return self.online.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return f"{self.id} ({self.get_online_count()})"