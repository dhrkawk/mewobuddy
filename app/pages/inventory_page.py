from __future__ import annotations

from typing import List, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFrame,
)


class ItemCard(QFrame):
    def __init__(self, item: Dict, locked: bool = False, equipped: bool = False, on_action=None):
        super().__init__()
        self.item = item
        self.locked = locked
        self.equipped = equipped
        self.on_action = on_action
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background: #fff; border: 1px solid #e5e5e8; border-radius: 12px;")
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout()
        img = QLabel()
        img.setStyleSheet("background:#eceff3; border-radius: 12px; min-height: 160px;")
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setText(self.item.get("name", ""))

        name = QLabel(self.item.get("name", ""))
        name.setStyleSheet("font-weight: 600;")
        price = QLabel(self.item.get("price", ""))
        price.setAlignment(Qt.AlignmentFlag.AlignRight)
        price.setStyleSheet("color: #7b1fa2;")

        btn = QPushButton()
        if self.locked:
            btn.setText("Purchase")
        else:
            btn.setText("Equipped" if self.equipped else "Equip")
            btn.setEnabled(not self.equipped)

        btn.clicked.connect(self._handle_action)

        layout.addWidget(img)
        header = QVBoxLayout()
        header.addWidget(name)
        header.addWidget(price)
        layout.addLayout(header)
        layout.addWidget(btn)
        self.setLayout(layout)

    def _handle_action(self):
        if self.on_action:
            self.on_action(self.item, self.locked)


class InventoryPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.owned_items: List[Dict] = []
        self.shop_items: List[Dict] = []
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout()
        owned_label = QLabel("My Items")
        owned_label.setStyleSheet("font-weight: 600; font-size: 16px;")
        layout.addWidget(owned_label)

        self.owned_grid = QGridLayout()
        self.owned_grid.setHorizontalSpacing(12)
        self.owned_grid.setVerticalSpacing(12)
        layout.addLayout(self.owned_grid)

        shop_label = QLabel("Shop")
        shop_label.setStyleSheet("font-weight: 600; font-size: 16px; margin-top:12px;")
        layout.addWidget(shop_label)

        self.shop_grid = QGridLayout()
        self.shop_grid.setHorizontalSpacing(12)
        self.shop_grid.setVerticalSpacing(12)
        layout.addLayout(self.shop_grid)

        layout.addStretch()
        self.setLayout(layout)

        self._load_mock_data()

    def _load_mock_data(self) -> None:
        self.owned_items = [
            {"id": "item1", "name": "Default Outfit", "equipped": True, "price": ""},
            {"id": "item2", "name": "Cat Ear Headband", "equipped": False, "price": ""},
            {"id": "item3", "name": "Cozy Winter Sweater", "equipped": False, "price": ""},
        ]
        self.shop_items = [
            {"id": "shop1", "name": "Holiday Dress", "price": "$499"},
            {"id": "shop2", "name": "Sparkling Hair Clip", "price": "$199"},
            {"id": "shop3", "name": "Gaming Headset", "price": "$799"},
            {"id": "shop4", "name": "Sakura Kimono", "price": "$899"},
        ]
        self.render()

    def render(self) -> None:
        # Owned
        for i in reversed(range(self.owned_grid.count())):
            item = self.owned_grid.itemAt(i).widget()
            if item:
                item.setParent(None)
        for idx, item in enumerate(self.owned_items):
            card = ItemCard(item, locked=False, equipped=item.get("equipped", False), on_action=self._on_own_action)
            self.owned_grid.addWidget(card, idx // 3, idx % 3)

        # Shop
        for i in reversed(range(self.shop_grid.count())):
            item = self.shop_grid.itemAt(i).widget()
            if item:
                item.setParent(None)
        for idx, item in enumerate(self.shop_items):
            card = ItemCard(item, locked=True, equipped=False, on_action=self._on_shop_action)
            self.shop_grid.addWidget(card, idx // 3, idx % 3)

    def _on_own_action(self, item: Dict, locked: bool) -> None:
        # Stub equip toggle: set this item equipped, others unequipped
        for i in self.owned_items:
            i["equipped"] = (i["id"] == item["id"])
        self.render()

    def _on_shop_action(self, item: Dict, locked: bool) -> None:
        # Stub purchase: move item to owned list, remove from shop
        self.shop_items = [i for i in self.shop_items if i["id"] != item["id"]]
        self.owned_items.append({"id": item["id"], "name": item["name"], "equipped": False, "price": ""})
        self.render()

    def set_data(self, owned: List[Dict], shop: List[Dict]) -> None:
        self.owned_items = owned
        self.shop_items = shop
        self.render()
