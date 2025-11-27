from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=20) 
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField(min_value=0)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.CharField(max_length=20),  
        required=False,
        default=list
    )
