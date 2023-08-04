from typing import List, Dict, Union

class TreeItem:
    def __init__(self, parent: "TreeItem" = None):
        self._parent = parent
        self._key = ""
        self._value = ""
        self._value_type = ""
        self._children = []

    def appendChild(self, item: "TreeItem"):
        self._children.append(item)

    def child(self, row: int) -> "TreeItem":
        return self._children[row]

    def parent(self) -> "TreeItem":
        return self._parent

    def childCount(self) -> int:
        return len(self._children)

    def row(self) -> int:
        return self._parent._children.index(self) if self._parent else 0

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, key: str):
        self._key = key

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    @property
    def value_type(self):
        return self._value_type

    @value_type.setter
    def value_type(self, value_type):
        self._value_type = value_type

    @classmethod
    def load(
        cls, value: Union[List, Dict], parent: "TreeItem" = None, sort=True
    ) -> "TreeItem":
        """Initial table initialization"""

        root_item = TreeItem(parent)
        root_item.key = "root"

        if isinstance(value, dict):
            items = list(value.items()) if sort else value.items()

            for key, value in items:
                child = cls.load(value, root_item)
                child.key = key
                child.value_type = type(value)
                root_item.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, root_item)
                child.key = index
                child.value_type = type(value)
                root_item.appendChild(child)

        else:
            root_item.value = value
            root_item.value_type = type(value)

        return root_item



