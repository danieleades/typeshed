import sys
import xml.dom.minidom
from _typeshed import Incomplete
from abc import abstractmethod
from collections.abc import Callable, Generator, Iterable, Iterator, Mapping, Sequence
from typing import Any, ClassVar, Literal, Protocol, SupportsIndex, TypeVar, overload
from typing_extensions import Self, TypeAlias

from docutils.transforms import Transform, Transformer
from docutils.utils import Reporter

_N = TypeVar("_N", bound=Node)

class _DomModule(Protocol):
    Document: type[xml.dom.minidom.Document]

# Functional Node Base Classes

class Node:
    # children is initialized by the subclasses
    children: Sequence[Node]
    # TODO: `parent` is actually `Element | None``, but `None`` only happens rarely,
    #       i.e. for synthetic nodes (or `document`, where it is overridden).
    #       See https://github.com/python/typeshed/blob/main/CONTRIBUTING.md#the-any-trick
    parent: Element | Any
    source: str | None
    line: int | None
    document: document | None
    def __bool__(self) -> Literal[True]: ...
    def asdom(self, dom: _DomModule | None = None) -> xml.dom.minidom.Element: ...
    # While docutils documents the Node class to be abstract it does not
    # actually use the ABCMeta metaclass. We still set @abstractmethod here
    # (although it's not used in the docutils implementation) because it
    # makes Mypy reject Node() with "Cannot instantiate abstract class".
    @abstractmethod
    def copy(self) -> Self: ...
    @abstractmethod
    def deepcopy(self) -> Self: ...
    @abstractmethod
    def pformat(self, indent: str = "    ", level: int = 0) -> str: ...
    @abstractmethod
    def astext(self) -> str: ...
    def setup_child(self, child: Node) -> None: ...
    def walk(self, visitor: NodeVisitor) -> bool: ...
    def walkabout(self, visitor: NodeVisitor) -> bool: ...
    @overload
    def findall(
        self, condition: type[_N], include_self: bool = True, descend: bool = True, siblings: bool = False, ascend: bool = False
    ) -> Generator[_N, None, None]: ...
    @overload
    def findall(
        self,
        condition: Callable[[Node], bool] | None = None,
        include_self: bool = True,
        descend: bool = True,
        siblings: bool = False,
        ascend: bool = False,
    ) -> Generator[Node, None, None]: ...
    @overload
    def traverse(
        self, condition: type[_N], include_self: bool = True, descend: bool = True, siblings: bool = False, ascend: bool = False
    ) -> list[_N]: ...
    @overload
    def traverse(
        self,
        condition: Callable[[Node], bool] | None = None,
        include_self: bool = True,
        descend: bool = True,
        siblings: bool = False,
        ascend: bool = False,
    ) -> list[Node]: ...
    @overload
    def next_node(
        self, condition: type[_N], include_self: bool = False, descend: bool = True, siblings: bool = False, ascend: bool = False
    ) -> _N: ...
    @overload
    def next_node(
        self,
        condition: Callable[[Node], bool] | None = None,
        include_self: bool = False,
        descend: bool = True,
        siblings: bool = False,
        ascend: bool = False,
    ) -> Node: ...

# Left out
# - def ensure_str (deprecated)
# - def unescape (canonical import from docutils.utils)

class Text(Node, str):
    tagname: ClassVar[str]
    children: tuple[()]

    # we omit the rawsource parameter because it has been deprecated and is ignored
    def __new__(cls, data: str) -> Self: ...
    def __init__(self, data: str) -> None: ...
    def shortrepr(self, maxlen: int = 18) -> str: ...
    def copy(self) -> Self: ...
    def deepcopy(self) -> Self: ...
    def pformat(self, indent: str = "    ", level: int = 0) -> str: ...
    def astext(self) -> str: ...
    def rstrip(self, chars: str | None = None) -> str: ...
    def lstrip(self, chars: str | None = None) -> str: ...

class Element(Node):
    children: list[Node]
    rawsource: str
    def __init__(self, rawsource: str = "", *children: Node, **attributes): ...
    def __len__(self) -> int: ...
    def __contains__(self, key: str | Node) -> bool: ...
    # '__iter__' is added as workaround, since mypy doesn't support classes that are iterable via '__getitem__'
    # see https://github.com/python/typeshed/pull/10099#issuecomment-1528789395
    def __iter__(self) -> Iterator[Node]: ...
    @overload
    def __getitem__(self, key: str) -> Any: ...
    @overload
    def __getitem__(self, key: int) -> Node: ...
    @overload
    def __getitem__(self, key: slice) -> list[Node]: ...
    @overload
    def __setitem__(self, key: str, item: Any) -> None: ...
    @overload
    def __setitem__(self, key: int, item: Node) -> None: ...
    @overload
    def __setitem__(self, key: slice, item: Iterable[Node]) -> None: ...
    def __delitem__(self, key: str | int | slice) -> None: ...
    def __add__(self, other: list[Node]) -> list[Node]: ...
    def __radd__(self, other: list[Node]) -> list[Node]: ...
    def __iadd__(self, other: Node | Iterable[Node]) -> Self: ...
    def copy(self) -> Self: ...
    def deepcopy(self) -> Self: ...
    def pformat(self, indent: str = "    ", level: int = 0) -> str: ...
    def astext(self) -> str: ...
    def index(self, item: Node, start: int = 0, stop: int = sys.maxsize) -> int: ...
    def remove(self, item: Node) -> None: ...
    def insert(self, index: SupportsIndex, item: Node | Iterable[Node] | None) -> None: ...
    def previous_sibling(self) -> Node | None: ...
    def __getattr__(self, __name: str) -> Incomplete: ...

class TextElement(Element):
    # A few classes not subclassing TextElement have this, too
    child_text_separator: ClassVar[str]
    def __init__(self, rawsource: str = "", text: str = "", *children: Node, **attributes) -> None: ...

class FixedTextElement(TextElement): ...

# Mixins

class Resolvable:
    resolved: int

class BackLinkable:
    def add_backref(self, refid: str) -> None: ...

# Element Categories

class Root: ...
class Titular: ...
class PreBibliographic: ...
class Bibliographic: ...
class Decorative(PreBibliographic): ...
class Structural: ...
class Body: ...
class General(Body): ...
class Sequential(Body): ...
class Admonition(Body): ...
class Special(Body): ...
class Invisible(PreBibliographic): ...
class Part: ...
class Inline: ...
class Referential(Resolvable): ...

class Targetable(Resolvable):
    referenced: int
    indirect_reference_name: str | None

class Labeled: ...

# Root Element

class document(Root, Structural, Element):
    parent: None
    transformer: Transformer
    def __init__(self, settings, reporter: Reporter, rawsource: str = "", *children: Node, **attributes) -> None: ...
    def __getattr__(self, __name: str) -> Incomplete: ...

# Title Elements

class title(Titular, PreBibliographic, TextElement): ...
class subtitle(Titular, PreBibliographic, TextElement): ...
class rubric(Titular, TextElement): ...

# Meta-Data Element

class meta(PreBibliographic, Element): ...

# Bibliographic Elements

class docinfo(Bibliographic, Element): ...
class author(Bibliographic, TextElement): ...
class authors(Bibliographic, Element): ...
class organization(Bibliographic, TextElement): ...
class address(Bibliographic, FixedTextElement): ...
class contact(Bibliographic, TextElement): ...
class version(Bibliographic, TextElement): ...
class revision(Bibliographic, TextElement): ...
class status(Bibliographic, TextElement): ...
class date(Bibliographic, TextElement): ...
class copyright(Bibliographic, TextElement): ...

# Decorative Elements

class decoration(Decorative, Element):
    def get_header(self) -> header: ...
    def get_footer(self) -> footer: ...

class header(Decorative, Element): ...
class footer(Decorative, Element): ...

# Structural Elements

class section(Structural, Element): ...
class topic(Structural, Element): ...
class sidebar(Structural, Element): ...
class transition(Structural, Element): ...

# Body Elements
# ===============

class paragraph(General, TextElement): ...
class compound(General, Element): ...
class container(General, Element): ...
class bullet_list(Sequential, Element): ...
class enumerated_list(Sequential, Element): ...
class list_item(Part, Element): ...
class definition_list(Sequential, Element): ...
class definition_list_item(Part, Element): ...
class term(Part, TextElement): ...
class classifier(Part, TextElement): ...
class definition(Part, Element): ...
class field_list(Sequential, Element): ...
class field(Part, Element): ...
class field_name(Part, TextElement): ...
class field_body(Part, Element): ...

# child_text_separator in some option* classes mirrors TextElement,
# but these classes do not subclass TextElement
class option(Part, Element):
    child_text_separator: str

class option_argument(Part, TextElement): ...

class option_group(Part, Element):
    child_text_separator: str  # see above

class option_list(Sequential, Element): ...

class option_list_item(Part, Element):
    child_text_separator: str  # see above

class option_string(Part, TextElement): ...
class description(Part, Element): ...
class literal_block(General, FixedTextElement): ...
class doctest_block(General, FixedTextElement): ...
class math_block(General, FixedTextElement): ...
class line_block(General, Element): ...

class line(Part, TextElement):
    indent: str | None

class block_quote(General, Element): ...
class attribution(Part, TextElement): ...
class attention(Admonition, Element): ...
class caution(Admonition, Element): ...
class danger(Admonition, Element): ...
class error(Admonition, Element): ...
class important(Admonition, Element): ...
class note(Admonition, Element): ...
class tip(Admonition, Element): ...
class hint(Admonition, Element): ...
class warning(Admonition, Element): ...
class admonition(Admonition, Element): ...
class comment(Special, Invisible, FixedTextElement): ...
class substitution_definition(Special, Invisible, TextElement): ...
class target(Special, Invisible, Inline, TextElement, Targetable): ...
class footnote(General, BackLinkable, Element, Labeled, Targetable): ...
class citation(General, BackLinkable, Element, Labeled, Targetable): ...
class label(Part, TextElement): ...
class figure(General, Element): ...
class caption(Part, TextElement): ...
class legend(Part, Element): ...
class table(General, Element): ...
class tgroup(Part, Element): ...
class colspec(Part, Element): ...
class thead(Part, Element): ...
class tbody(Part, Element): ...
class row(Part, Element): ...
class entry(Part, Element): ...

class system_message(Special, BackLinkable, PreBibliographic, Element):
    def __init__(self, message: str | None = None, *children: Node, **attributes) -> None: ...

class pending(Special, Invisible, Element):
    transform: Transform
    details: Mapping[str, Any]
    def __init__(
        self, transform: Transform, details: Mapping[str, Any] | None = None, rawsource: str = "", *children: Node, **attributes
    ) -> None: ...

class raw(Special, Inline, PreBibliographic, FixedTextElement): ...

# Inline Elements

class emphasis(Inline, TextElement): ...
class strong(Inline, TextElement): ...
class literal(Inline, TextElement): ...
class reference(General, Inline, Referential, TextElement): ...
class footnote_reference(Inline, Referential, TextElement): ...
class citation_reference(Inline, Referential, TextElement): ...
class substitution_reference(Inline, TextElement): ...
class title_reference(Inline, TextElement): ...
class abbreviation(Inline, TextElement): ...
class acronym(Inline, TextElement): ...
class superscript(Inline, TextElement): ...
class subscript(Inline, TextElement): ...
class math(Inline, TextElement): ...
class image(General, Inline, Element): ...
class inline(Inline, TextElement): ...
class problematic(Inline, TextElement): ...
class generated(Inline, TextElement): ...

# Auxiliary Classes, Functions, and Data

node_class_names: list[str]

# necessary to disambiguate type and field in NodeVisitor
_Document: TypeAlias = document

class NodeVisitor:
    optional: ClassVar[tuple[str, ...]]
    document: _Document
    def __init__(self, document: _Document) -> None: ...
    def dispatch_visit(self, node: Node) -> Any: ...
    def dispatch_departure(self, node: Node) -> Any: ...
    def unknown_visit(self, node: Node) -> Any: ...
    def unknown_departure(self, node: Node) -> Any: ...

class SparseNodeVisitor(NodeVisitor): ...

class GenericNodeVisitor(NodeVisitor):
    # all the visit_<node_class_name> methods
    def __getattr__(self, __name: str) -> Incomplete: ...

class TreeCopyVisitor(GenericNodeVisitor):
    parent_stack: list[Node]
    parent: list[Node]
    def get_tree_copy(self) -> Node: ...

class TreePruningException(Exception): ...
class SkipChildren(TreePruningException): ...
class SkipSiblings(TreePruningException): ...
class SkipNode(TreePruningException): ...
class SkipDeparture(TreePruningException): ...
class NodeFound(TreePruningException): ...
class StopTraversal(TreePruningException): ...

def make_id(string: str) -> str: ...
def dupname(node: Node, name: str) -> None: ...
def fully_normalize_name(name: str) -> str: ...
def whitespace_normalize_name(name: str) -> str: ...
def serial_escape(value: str) -> str: ...
def pseudo_quoteattr(value: str) -> str: ...
