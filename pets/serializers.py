from .models import Sex
from rest_framework import serializers
from groups.serializers import GroupSerializer
from traits.serializers import TraitSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    age = serializers.IntegerField()
    weight = serializers.DecimalField(max_digits=4, decimal_places=1)
    sex = serializers.ChoiceField(choices=Sex.choices, default=Sex.DEFAULT)
    group = GroupSerializer()
    traits = TraitSerializer(many=True)