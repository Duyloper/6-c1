#1c 2d 3c 4a 5b 6c 7d 8d 9c 10d
# -0.25d
import sys
import json
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget

class Homework:
    def __init__(self, name, priority, completed=False):
        self.name = name
        self.priority = priority
        self.completed = completed

    def to_dict(self):
        return {
            "name": self.name,
            "priority": self.priority,
            "completed": self.completed
        }


class HomeworkList:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def all_completed(self):
        completed = True
        for item in self.items:
            if item.completed == False:
                completed = False
            print(item.name)
        if completed:
            print("All finished!")

    def export_to_json(self, filename="new_data.json"):
        data = [item.to_dict() for item in self.items]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

class MainWindow(QMainWindow):
    def __init__(self, hw_list):
        super().__init__()

        # Load giao diện từ file .ui (phải nằm cùng thư mục với file .py này)
        uic.loadUi("untitled.ui", self)

        self.hw_list = hw_list

        # Nếu giao diện chưa có listWidget, tạo widget mới
        if not hasattr(self, "listWidget"):
            self.listWidget = QListWidget(self)
            self.listWidget.setGeometry(20, 20, 760, 280)

        # Hiển thị tên các bài tập lên listWidget
        for item in self.hw_list.items:
            self.listWidget.addItem(item.name)

        # Gắn sự kiện cho nút pushButton ("export data")
        self.pushButton.clicked.connect(self.export_data)

    def export_data(self):
        self.hw_list.export_to_json("new_data.json")
        print("Đã xuất dữ liệu ra new_data.json")

if __name__ == "__main__":
    hw_list = HomeworkList()
    hw_list.add_item(Homework("Lap trinh App Producer", 3))
    hw_list.add_item(Homework("Lam van", 2, True))
    hw_list.add_item(Homework("Lap trinh GameMaker", 3))

    app = QApplication(sys.argv)
    window = MainWindow(hw_list)
    window.show()
    sys.exit(app.exec())