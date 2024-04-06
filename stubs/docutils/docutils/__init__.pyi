from collections.abc import Callable, Sequence
from typing import Any, ClassVar, NamedTuple
from typing_extensions import Self

from docutils.transforms import Transform
from docutils.nodes import Node

__docformat__: str
__version__: str

class _VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int
    release: bool

class VersionInfo(_VersionInfo):
    def __new__(
        cls, major: int = 0, minor: int = 0, micro: int = 0, releaselevel: str = "final", serial: int = 0, release: bool = True
    ) -> Self: ...

__version_info__: VersionInfo
__version_details__: str

class ApplicationError(Exception): ...
class DataError(ApplicationError): ...

class SettingsSpec:
    settings_spec: ClassVar[tuple[Any, ...]]
    settings_defaults: ClassVar[dict[Any, Any] | None]
    settings_default_overrides: ClassVar[dict[Any, Any] | None]
    relative_path_settings: ClassVar[tuple[Any, ...]]
    config_section: ClassVar[str | None]
    config_section_dependencies: ClassVar[tuple[str, ...] | None]

class TransformSpec:
    def get_transforms(self) -> list[type[Transform]]: ...
    default_transforms: ClassVar[tuple[Any, ...]]
    unknown_reference_resolvers: ClassVar[Sequence[Callable[[Node], bool]]]

ComponentType = Literal["reader", "parser", "writer"]

class Component(SettingsSpec, TransformSpec):
    component_type: ClassVar[ComponentType | None]
    supported: ClassVar[tuple[str, ...]]
    def supports(self, format: str) -> bool: ...
