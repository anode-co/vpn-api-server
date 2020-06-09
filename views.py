from simplecgi import (
    Response
)
import json
from models import (
    Person,
    CjdnsClientPublicKey,
    CjdnsIpAddress,
)
from serializers import (
    PersonSerializer,
    PersonListSerializer,
    CjdnsClientPublicKeySerializer,
)


class AuthorizeClientView:
    """Handle HTTP Requests."""

    database_manager = None
    route_manager = None
    headers = {
        'Content-Type': 'application/json; encoding=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }

    def __init__(self, database_manager, route_manager):
        """Initialize."""
        self.database_manager = database_manager
        self.route_manager = route_manager
        self.route_manager.preload_allocations()

    def post(self, request):
        """POST handler."""
        # person = Person.get(self.database_manager, id=1)
        # processor = PersonSerializer(person)
        # output_json = processor.to_json()
        print("POST")
        print("fetching authorization")
        body_json = request.body_json
        input_processor = CjdnsClientPublicKeySerializer(self.database_manager, body_json)

        print(body_json)
        print(input_processor)

        errors = input_processor.check_json()
        print(errors)
        if len(errors) > 0:
            print("errors were found")
            output = dict([(error, "This field is required") for error in errors])
            return Response(output, status=Response.STATUS_400_BAD_REQUEST, headers=self.headers)

        cjdns_public_key = None
        allocations = []

        input_cjdns_public_key = input_processor.to_object()
        # try to fetch existing object
        http_status = Response.STATUS_200_OK
        try:
            cjdns_public_key = CjdnsClientPublicKey.get(self.database_manager, client_public_key=input_cjdns_public_key.client_public_key)
            http_status = Response.STATUS_201_CREATED
        except CjdnsClientPublicKey.NoneFoundException:
            cjdns_public_key = input_cjdns_public_key
            cjdns_public_key.create()

        print("cjdns_public_key object")
        print(cjdns_public_key)
        try:
            allocations = self.route_manager.allocate(cjdns_public_key)
        except self.route_manager.OutOfAvailableAddressesException:
            return Response({'status': 'error', 'message': 'out of available addresses'}, status=Response.STATUS_403_DENIED, headers=self.headers)

        print("allocations:")
        print(allocations)

        return Response({'status': 'success', 'message': 'client authorized'}, status=http_status, headers=self.headers)

    def delete(self, request):
        """DELETE handler."""
        print("DELETE")
        print("fetching authorization")
        body_json = request.body_json
        input_processor = CjdnsClientPublicKeySerializer(self.database_manager, body_json)

        errors = input_processor.check_json()
        print(errors)
        if len(errors) > 0:
            print("errors were found")
            output = dict([(error, "This field is required") for error in errors])
            return Response(output, status=Response.STATUS_400_BAD_REQUEST, headers=self.headers)

        input_cjdns_public_key = input_processor.to_object()
        try:
            cjdns_public_key = CjdnsClientPublicKey.get(self.database_manager, client_public_key=input_cjdns_public_key.client_public_key)
            CjdnsIpAddress.delete(self.database_manager, cjdns_client_public_key_id=cjdns_public_key.id)
            CjdnsClientPublicKey.delete(self.database_manager, id=cjdns_public_key.id)
            return Response({'status': 'success', 'message': 'public key deleted'}, headers=self.headers)
        except CjdnsClientPublicKey.NoneFoundException:
            return Response({'status': 'error', 'message': 'not found'}, status=Response.STATUS_404_NOT_FOUND, headers=self.headers)


class PersonView:
    """Handle HTTP Requests."""

    database_manager = None
    headers = {
        'Content-Type': 'application/json; encoding=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }

    def __init__(self, database_manager):
        """Initialize."""
        self.database_manager = database_manager

    def get(self, request):
        """GET handler."""
        print("GET")
        print("fetching people")
        people = Person.Curator.fetch(Person, self.database_manager)
        print(people)
        people_serializer = PersonListSerializer(self.database_manager, people)
        print(people_serializer)
        print(people_serializer.to_json())
        return Response(people_serializer.to_json(), headers=self.headers)

    def post(self, request):
        """POST handler."""
        # person = Person.get(self.database_manager, id=1)
        # processor = PersonSerializer(person)
        # output_json = processor.to_json()
        print("POST")
        input_processor = PersonSerializer(self.database_manager, request.body_json)
        errors = input_processor.check_json()
        print("JSON Errors:")
        print(errors)
        if len(errors) == 0:
            # new_person = input_processor.to_object()
            new_person = input_processor.save_object()
            print(new_person)
        else:
            output = dict([(error, "This field is required") for error in errors])
            return Response(output, status=Response.STATUS_400_BAD_REQUEST, headers=self.headers)
        # print("PERSON as JSON:")
        # print(json.dumps(output_json, indent=4))
        print("POST")
        print(request)
        print(self.headers)
        body = request.body
        print("BODY:")
        print(body)
        print(json.dumps(request.body_json, indent=4))
        # input_processor = PersonSerializer(request.body_json)

        response = Response(input_processor.to_json(), headers=self.headers)
        return response
