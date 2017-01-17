from rest_framework import serializers
from .models        import Client, Command, Result

class ResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Result
        fields = ('command', 'data', 'created')

class CommandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Command
        fields = ('client', 'name', 'created')

class ClientSerializer(serializers.HyperlinkedModelSerializer):
        
    #commands = CommandSerializer(many=True, read_only=True)
    commands = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ('name', 'created', 'last_connected', 'commands')

