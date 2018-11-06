from .error import *
from django.core import exceptions
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from ..models import Reservation
from ..tasks import cancelled
from ..serializers import ReservationPOSTSerializer, ReservationGETSerializer
import datetime


def reservationIdExists(id):
    try:
        reservation = Reservation.objects.get(id=id)
    except exceptions.ObjectDoesNotExist:
        return False
    return reservation


class ReservationView(APIView):

    # Gets list of all reservations or specific reservations, depending on parameters
    def get(self, request):
        # Look for the following parameters in GET request
        ID = request.query_params.get("id", None)
        email = request.query_params.get("email", None)
        startDate = request.query_params.get("from", None)
        endDate = request.query_params.get("to", None)

        res = Reservation.objects.all()

        # Error check the dates to be in YYYY-MM-DD
        if startDate is not None:
            try:
                datetime.datetime.strptime(startDate, '%Y-%m-%d')
            except ValueError:
                return RespError(400, "startDate is in an invalid date format. Make sure it's in the YYYY-MM-DD format.")
        if endDate is not None:
            try:
                datetime.datetime.strptime(endDate, '%Y-%m-%d')
            except ValueError:
                return RespError(400, "endDate is in an invalid date format. Make sure it's in the YYYY-MM-DD format.")

        # Find a single reservation with a specific ID, associated with by a specific email
        if ID and email:
            res = res.filter(id=ID, email=email)
            if not res:
                return RespError(404, "No reservation with this ID and email were found.")

        # Find all reservations in a specific date range if only the start and end dates are given
        elif (startDate and endDate) and not (ID or email):
            res = res.filter(startDate__gte=startDate).filter(endDate__lte=endDate)

        # Find all reservations made by a certain email address in a certain date range
        elif startDate and endDate and email and (not ID):
            res = res.filter(startDate__gte=startDate).filter(endDate__lte=endDate).filter(email=email)

        # Find all reservations made by a certain email address
        elif email and not (ID or startDate or endDate):
            res = res.filter(email=email)

        # Find ALL reservations if all parameters are missing
        elif not ID and not email and not startDate and not endDate:
            pass

        # if there is some other combination of parameters in the get request, return error
        else:
            return RespError(400, "Invalid combination of query parameters.")

        # Success: return requested data in GET request
        serial = ReservationGETSerializer(res, many=True)
        return Response({"data": serial.data})


    # Attempt to create a new reservation
    def post(self, request):
        newRes = request.data

        properties = {
            "email": False,
            "licenseName": False,
            "licenseAddress": False,
            "startDate": False,
            "endDate": False,
            "gear": False,
            "status": False
        }

        # check for extra unnecessary keys
        for key in newRes:
            if key not in properties:
                return RespError(400, "'" + str(key) + "' is not valid with this POST method, please resubmit the"
                                                       " request without it.")

        sRes = ReservationPOSTSerializer(data=newRes)

        if not sRes.is_valid():
            return serialValidation(sRes)

        sRes.save()

        return Response(sRes.data)

    # Edit gear in reservation
    def patch(self, request):
        request = request.data
        allowedPatchMethods = {
            "gear": True,
        }

        idToUpdate = request.get("id", None)
        expectedVersion = request.get("expectedVersion", None)
        patch = request.get("patch", None)

        # The following 3 checks could be up-leveled to a generic PATCH-check function
        if not idToUpdate:
            return RespError(400, "You must specify an id to patch.")

        if not expectedVersion:
            return RespError(400, "You must specify an 'expectedVersion'.")

        if not patch:
            return RespError(400, "You must specify a 'patch' object with methods.")

        for key in patch:
            if key not in allowedPatchMethods:
                return RespError(400, "'" + key + "' is not a valid patch method.")

        try:
            resv = Reservation.objects.get(id=idToUpdate)
        except Reservation.DoesNotExist:
            return RespError(400, "There is no reservation with the id '" + str(idToUpdate) + "'")

        # Check if reservation gear can be modified based on status
        if resv.status not in ["REQUESTED", "APPROVED"]:
            return RespError(400, "The reservation status must be REQUESTED or APPROVED to be modified")

        for field in resv._meta.fields: # field = Api.Reservation.fieldName
            f = str(field)
            f = f[16:]  # truncates Api.Reservation. part out
            if f != "gear":
                patch[f] = getattr(resv, f)

        sResv = ReservationPOSTSerializer(resv, data=patch)

        if not sResv.is_valid():
            return serialValidation(sResv)

        resv.version += 1
        sResv.save()

        return Response(sResv.data)


@api_view(['POST'])
def checkin(request):
    request = request.data

    if not request['id']:
        return RespError(400, "You must specify an id to return.")

    reservation = reservationIdExists(request['id'])
    if not reservation:
        return RespError(400, "There is no reservation with the id of '" + str(request['id']) + "'")

    reservation.status = "RETURNED"
    reservation.save()

    return Response()


@api_view(['POST'])
def cancel(request):
    request = request.data

    if not request['id']:
        return RespError(400, "You must specify an id to return.")

    reservation = reservationIdExists(request['id'])
    if not reservation:
        return RespError(400, "There is no reservation with the id of '" + str(request['id']) + "'")

    if reservation.status != "REQUESTED" and reservation.status != "APPROVED":
        return RespError(400, "The reservation status must be REQUESTED or APPROVED")

    reservation.status = "CANCELLED"
    reservation.save()

    cancelled(reservation)

    return Response()