from django.shortcuts import render, get_object_or_404

from rest_framework.views import APIView, Response, Request, status
from rest_framework.pagination import PageNumberPagination
from .serializers import PetSerializer
from groups.models import Group
from traits.models import Trait
from .models import Pet

# Create your views here.
class PetView(APIView, PageNumberPagination):
    # Cria um novo PET
    def post(self, request: Request) -> Response:

        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_list = serializer.validated_data.pop("group")
        traits_list = serializer.validated_data.pop("traits")

        group_obj = Group.objects.filter(
            scientific_name__iexact=group_list["scientific_name"]
        ).first()

        if not group_obj:
            group_obj = Group.objects.create(**group_list)

        pet: Pet = Pet.objects.create(
            **serializer.validated_data, group=group_obj)

        for trait_dict in traits_list:
            trait_obj = Trait.objects.filter(
                name__iexact=trait_dict["name"]
            ).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait_dict)

            pet.traits.add(trait_obj)

        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_201_CREATED)

    # Lista todos os pets cadastrados
    def get(self, request):
        pets = Pet.objects.all()
        page = self.paginate_queryset(pets)

        if page is not None:
            serializer = PetSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data)

class PetDetailView(APIView):
    # Retorna um pet específico
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(pet)

        return Response(serializer.data, status.HTTP_200_OK)

    # Atualiza um pet específico
    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(pet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        traits_data = serializer.validated_data.pop("traits", None)
        group_data = serializer.validated_data.pop("group", None)

        for key in serializer.validated_data.keys():
            if key in ['name', 'age', 'color']:
                setattr(pet, key, serializer.validated_data[key])

        new_traits_list = []

        if traits_data:
            for trait in traits_data:
                trait_exist = Trait.objects.filter(name__icontains=trait["name"])
                trait_obj = trait_exist.first() if trait_exist.exists() else Trait.objects.create(name=trait["name"].lower())
                new_traits_list.append(trait_obj)

            pet.traits.set(new_traits_list)

        if group_data:
            group_exist = Group.objects.filter(scientific_name__icontains=group_data["scientific_name"])
            group_obj = group_exist.first() if group_exist.exists() else Group.objects.create(scientific_name=group_data["scientific_name"].lower())
            pet.group = group_obj

        pet.save()

        serializer = PetSerializer(pet)

        return Response(serializer.data, status=status.HTTP_200_OK)