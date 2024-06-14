from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ConfigScopeFields:
    scope: str
    required: List[str]
    optional: List[str]


class ConfigContextInterface(ABC):
    @abstractmethod
    def get_sender_fields(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_message_fields(self) -> Dict[str, Any]:
        pass


class ConfigContext(ConfigContextInterface):

    SENDER_FIELDS = ConfigScopeFields(
        "sender fields",
        required=[
            "username",
            "password",
            "host",
            "port",
        ],
        optional=[
            "tls",
        ],
    )

    MESSAGE_FIELDS = ConfigScopeFields(
        "sender fields",
        required=[],
        optional=[
            "provider",
        ],
    )

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def create_kwargs(self, scope_fields: ConfigScopeFields):
        kwargs = {}
        for field in scope_fields.required:
            kwargs[field] = self.config[field]

        for field in scope_fields.optional:
            if field in self.config:
                kwargs[field] = self.config[field]
        return kwargs

    def mournful_create_kwargs(self, scope_fields: ConfigScopeFields):
        try:
            return self.create_kwargs(scope_fields)
        except:
            raise ConfigException(scope_fields, self.config)

    def get_sender_fields(self) -> Dict[str, Any]:
        return self.mournful_create_kwargs(self.SENDER_FIELDS)

    def get_message_fields(self) -> Dict[str, Any]:
        return self.mournful_create_kwargs(self.MESSAGE_FIELDS)


class ConfigException(Exception):
    def get_message(self):
        return "\n".join(
            [
                f"Mismatch fields in the configuration for `{self.scope_fields.scope}`",
                f"Required Fields: {self.scope_fields.required}",
                f"Optional Fields: {self.scope_fields.optional}",
                f"Provided Fields: {list(self.config.keys())}",
            ]
        )

    def __init__(self, scope_fields: ConfigScopeFields, config: Dict[str, Any]) -> None:
        self.scope_fields = scope_fields
        self.config = config
        super().__init__(self.get_message())
