"""
Neo4j graph node models.

Example models for representing graph data structures.
"""

from typing import Any


class Person:
    """
    Example Person node for graph database.

    This is a simple dictionary-based representation.
    For more advanced usage, consider using neomodel OGM.
    """

    def __init__(self, name: str, age: int | None = None, **kwargs: Any):
        self.name = name
        self.age = age
        self.properties = kwargs

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Neo4j."""
        data = {"name": self.name}
        if self.age is not None:
            data["age"] = self.age
        data.update(self.properties)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Person":
        """Create Person from dictionary."""
        name = data.pop("name")
        age = data.pop("age", None)
        return cls(name=name, age=age, **data)


class Relationship:
    """
    Example relationship between nodes.
    """

    def __init__(
        self,
        type_: str,
        from_node: str,
        to_node: str,
        properties: dict[str, Any] | None = None,
    ):
        self.type = type_
        self.from_node = from_node
        self.to_node = to_node
        self.properties = properties or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Neo4j."""
        return {
            "type": self.type,
            "from": self.from_node,
            "to": self.to_node,
            "properties": self.properties,
        }
