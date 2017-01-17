from common       import utils
from django.db    import models
from django.utils import timezone

class Client(models.Model):

    name           = models.CharField(max_length=20)
    created        = models.DateTimeField()
    last_connected = models.DateTimeField()

    def __str__(self):
        return self.name
    
    @classmethod
    def create(cls, name):
        return cls(
            name           = name,
            created        = utils.now().isoformat(),
            last_connected = utils.now().isoformat(),
        )

    def update_last_connected(self):
        self.last_connected = utils.now().isoformat()
        self.save()
        return self

    def time_since_connected(self):
        now = timezone.now()
        return now - last_connected

class Command(models.Model):

    client  = models.ForeignKey(Client)
    name    = models.CharField(max_length=200)
    created = models.DateTimeField()
   
    def __str__(self):
        return self.name
 
class Result(models.Model):
    
    command = models.ForeignKey(Command)
    data    = models.CharField(max_length=200)
    created = models.DateTimeField()

    def __str__(self):
        return self.pk
