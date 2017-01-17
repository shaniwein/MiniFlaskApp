from django.utils   import timezone
from django.views   import generic
from rest_framework import viewsets
from .models        import Client, Command, Result
from .serializers   import ClientSerializer, CommandSerializer, ResultSerializer

class IndexView(generic.ListView):

    template_name       = 'website/clients.html'
    context_object_name = 'latest_clients_list'

    def get_queryset(self):
        return Client.objectes.filter(
            created__lte=timezone.now()
        ).order_by('-created')[:10]

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('-created')
    serializer_class = ClientSerializer 

class CommandViewSet(viewsets.ModelViewSet):
    queryset = Command.objects.all().order_by('-created')
    serializer_class = CommandSerializer

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all().order_by('-created')
    serializer_class = ResultSerializer 
