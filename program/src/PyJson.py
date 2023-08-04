from typing import Any
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt

from src.Tree import TreeItem

class JsonModel(QAbstractItemModel):
    def __init__(self, parent: QObject = None, main_window: QObject = None ):
        super().__init__(parent)
        self._main_window = main_window
        self._rootItem = TreeItem()
        self._headers = ("key", "value", "type")

    def clear(self):
        self.load({})

    def load(self, document: dict):
        assert isinstance(
            document, (dict, list, tuple)
        ), "`document` must be of dict, list or tuple, " f"not {type(document)}"

        self.beginResetModel()
        self._rootItem = TreeItem.load(document)
        self._rootItem.value_type = type(document)
        self.endResetModel()

        return True

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """Table initialization"""

        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.key

            if index.column() == 1:
                return item.value

            if index.column() == 2:
                if item.value != '':
                    return str(type(item.value)).split("'")[1]

        elif role == Qt.EditRole:
            if index.column() == 1:
                return item.value

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole):
        """Called whenever a value in a cell changes. This is where the table is edited"""

        if role == Qt.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                item.value = value

                self.dataChanged.emit(item, item.value, [Qt.EditRole])
                self._main_window.resizeInputColoumnNumberOne()

            return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        """Initializes the table header"""

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self._rootItem
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)

        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self._rootItem:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self._rootItem
        else:
            parent_item = parent.internalPointer()

        return parent_item.childCount()

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super(JsonModel, self).flags(index)

        if index.column() == 1:
            return Qt.ItemIsEditable | flags
        else:
            return flags

    def toJson(self, item=None):
        """Creating a json file based on a dictionary"""

        if item is None:
            item = self._rootItem

        n_child = item.childCount()

        if item.value_type is dict:
            document = {}
            for i in range(n_child):
                ch = item.child(i)
                document[ch.key] = self.toJson(ch)
            return document

        elif item.value_type == list:
            document = []
            for i in range(n_child):
                ch = item.child(i)
                document.append(self.toJson(ch))
            return document

        else:
            return item.value

