from common       import utils
from django.db    import models
from django.utils import timezone

class Client(models.Model):

    name           = models.CharField(max_length=20)
    created        = models.DateTimeField(auto_now_add=True)
    last_connected = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def update_last_connected(self):
        self.save()
        return self

    def time_since_connected(self):
        return utils.now() - last_connected

class Command(models.Model):

    client  = models.ForeignKey(Client, related_name='commands')
    name    = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
   
    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return '%d: %s' % (self.pk, self.name)

class Result(models.Model):
    
    command = models.ForeignKey(Command)
    data    = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)
