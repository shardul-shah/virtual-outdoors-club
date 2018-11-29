from ..models import GearCategory
from django.core import exceptions
from ..serializers import GearCategorySerializer
from .error import *
from django.db.models import ProtectedError
from rest_framework.views import APIView


class GearCategoryView(APIView):
    def get(self, request):
        categories = GearCategory.objects.all()
        categories = GearCategorySerializer(categories, many=True)

        return Response({"data": categories.data})

    # handles addition of a gear category
    def post(self, request):
        newGearCategory = request.data

        if "name" not in newGearCategory:
            return RespError(400, "You are required to provide a name for a gear category")

        try:
            newGearCategory["name"] = newGearCategory["name"].title()
        except AttributeError:
            return RespError(400, "Gear category name needs to be a string")

        serial = GearCategorySerializer(data=newGearCategory)
        
        # check for invalid serial, i.e. malformed request
        if not serial.is_valid():
            return serialValidation(serial)

        serial.save()

        return Response(serial.validated_data)

    def patch(self, request):
        request = request.data

        currentName = request.get("name", None)
        patch = request.get("patch", None)

        if not currentName:
            return RespError(400, "You must specify a category to patch.")

        if not patch:
            return RespError(400, "You must specify a 'patch' object with attributes to patch.")

        newName = patch.get("name")

        if not newName:
            return RespError(400, "You must specify a new name to update to.")

        try:
            newName = newName.title()
            currentName = currentName.title()
        except AttributeError:
            return RespError(400, "Gear category names must be a string")

        try:
            gear_category = GearCategory.objects.get(name=currentName)
        except GearCategory.DoesNotExist:
            return RespError(400, "Gear category '" + currentName + "' does not exist")

        try:
            GearCategory.objects.get(name=newName)
        except GearCategory.DoesNotExist:
            pass
        else:
            return RespError(400, "name: gear category with this name already exists.")

        # check validity
        serial = GearCategorySerializer(gear_category, data=patch)
        if not serial.is_valid():
            return serialValidation(serial)

        serial.save()

        return Response({"name": newName})

    # handles deletion of a gear category
    def delete(self, request):
        nameToDelete = request.query_params.get("name", None)
        if not nameToDelete:
            return RespError(400, "You must specify a 'name' parameter to delete.")

        # try to delete the category
        try:
            GearCategory.objects.get(name=nameToDelete).delete()
        except ProtectedError:
            return RespError(409, "You cannot remove a gear category that is currently being referenced by a piece of gear.")
        except exceptions.ObjectDoesNotExist:
            return RespError(400, "The gear category '" + nameToDelete + "' does not exist so it cannot be deleted.")
               
        return RespError(200, "Deleted the category: '" + nameToDelete + "'")
