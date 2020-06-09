from simplerestapi import (
    JsonObjectSerializer,
    JsonListSerializer,
)
from models import (
    Person,
    CjdnsClientPublicKey,
    CjdnsIpAddress
)


class PersonSerializer(JsonObjectSerializer):
    """Serialize a Person."""

    model = Person
    properties = [
        'name',
        'age'
    ]


class PersonListSerializer(JsonListSerializer):
    """Serialize a Person list."""

    serializer = PersonSerializer
    model = Person
    properties = [
        'name',
        'age'
    ]


class CjdnsClientPublicKeySerializer(JsonObjectSerializer):
    """Serialize a Person."""

    model = CjdnsClientPublicKey
    properties = [
        'client_public_key',
    ]


class CjdnsIpAddressSerializer(JsonObjectSerializer):
    """Serialize a Person."""

    model = CjdnsIpAddress
    properties = [
        'ip_address'
    ]
