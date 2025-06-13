import sys
import csv
import os

from PyQt5.QtWidgets import(
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QComboBox,
    QDateEdit,
    QGroupBox,
    QHeaderView,
    QDateTimeEdit,
    QHBoxLayout,
    QTimeEdit
)

from PyQt5.QtCore import QDate, QTimer, QTime, Qt
from PyQt5.QtGui import QFont, QBrush, QColor, QIcon

from plyer import notification

CSV_FILE = "tasks.csv"

class TaskReminderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Task Reminder")
        self.setWindowIcon(QIcon("app_icon.png"))
        self.setGeometry(300,100,750,620)
        self.setupUI()
        self.notified_tasks = set()  
        self.csv_file = "tasks.csv"
        self.startReminderTimer()

    def setupUI(self):

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f7;
                font-family: Segoe UI;
            }
            QGroupBox {
                border: 2px solid #ccc;
                border-radius: 12px;
                margin-top: 10px;
                background: rgba(255, 255, 255, 0.9);
                font-weight: bold;
            }
            QGroupBox::title {
                           subcontrol-origin:margin;
                           subcontrol-position:top center;
                           padding:0 3px;
                           background-color: lightgray;
                           }

            QLineEdit, QComboBox, QDateEdit, QTimeEdit {
                padding: 6px;
                border-radius: 8px;
                border: 1px solid #aaa;
                font-size: 14px;
            }
            QPushButton {
                padding: 6px 14px;
                border-radius: 8px;
                background-color: #2c7be5;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a66cc;
            }
            QTableWidget {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QHeaderView::section {
                background-color: #2c7be5;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
        """)


        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        heading = QLabel("🗓️ Daily Task Reminder")
        heading.setFont(QFont("Segoe UI", 26, QFont.Bold))
        heading.setStyleSheet("color:#2c7be5;")
        heading.setAlignment(Qt.AlignCenter)
        layout.addWidget(heading)

        entry_box = QGroupBox("Add New Task")
        entry_box_layout = QVBoxLayout()

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter your Task")
        entry_box_layout.addWidget(self.task_input)

        self.category_input = QComboBox(editable=True,insertPolicy=QComboBox.InsertAtTop)
        self.category_input.addItems(["Work", "Personal", "Study", "Other"])
        entry_box_layout.addWidget(self.category_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        entry_box_layout.addWidget(self.date_input)

        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setDisplayFormat("hh:mm AP")
        entry_box_layout.addWidget(self.time_input)

        add_task = QPushButton("✚ Add Task")
        add_task.clicked.connect(self.addTask)
        entry_box_layout.addWidget(add_task)

        entry_box.setLayout(entry_box_layout)
        layout.addWidget(entry_box)


        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(["Task", "Category", "Due Date", "Time", "Status", "Actions"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.task_table)


        self.setLayout(layout)


        def csv_file(self):
          if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, "w", newline="") as file:
                pass

    def addTask(self):
        task = self.task_input.text().strip()
        category = self.category_input.currentText()
        date = self.date_input.date().toString("dd/MM/yyyy")
        time = self.time_input.time().toString("HH:mm")
        status = "pending"

        if task =="":
            QMessageBox.warning(self, "Missing Task", "Please enter a Task Name")
            return
        
        with open(CSV_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([task,category,date,time,status])

        self.task_input.clear()
        self.loadTasks()

    def loadTasks(self):
        self.task_table.setRowCount(0)

        with open(CSV_FILE, "r") as file:
            reader = csv.reader(file)
            for rowIndex, row in enumerate(reader):
                if len(row) < 5:
                    continue
                task, category, date, time, status = row
                self.task_table.insertRow(rowIndex)

                for colIndex, value in enumerate([task, category, date, time, status]):
                    item = QTableWidgetItem(value)
                    if status == "done":
                        item.setForeground(QBrush(QColor("green")))
                        font = item.font()
                        font.setStrikeOut(True)
                        item.setFont(font)
                    elif status == "pending" and QDate.fromString(date, "dd/MM/yyyy") < QDate.currentDate():
                        item.setForeground(QBrush(QColor("red")))
                    self.task_table.setItem(rowIndex, colIndex, item)

                markBtn = QPushButton("✔ Done")
                delBtn = QPushButton("🗑 Delete")
                markBtn.clicked.connect(lambda _, r=rowIndex: self.markAsDone(r))
                delBtn.clicked.connect(lambda _, r=rowIndex: self.deleteTask(r))

                hBox = QHBoxLayout()
                hBox.addWidget(markBtn)
                hBox.addWidget(delBtn)
                hBox.setContentsMargins(0, 0, 0, 0)

                actionWidget = QWidget()
                actionWidget.setLayout(hBox)
                self.task_table.setCellWidget(rowIndex, 5, actionWidget)

    def markAsDone(self, row):
        tasks = self.readTasks()
        if 0 <= row < len(tasks):
            tasks[row][4] = "done"
            self.writeTasks(tasks)
            self.loadTasks()

    def deleteTask(self, row):
        tasks = self.readTasks()
        if 0 <= row < len(tasks):
            del tasks[row]
            self.writeTasks(tasks)
            self.loadTasks()

    def readTasks(self):
        with open(CSV_FILE, "r") as file:
            return [row for row in csv.reader(file) if len(row) >= 5]

    def writeTasks(self, tasks):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(tasks)

    def startReminderTimer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.showTodayReminders)
        timer.start(60000)
        self.showTodayReminders()

    def showTodayReminders(self):
        current_date = QDate.currentDate().toString("dd/MM/yyyy")
        current_time = QTime.currentTime().toString("HH:mm")

        tasks = self.readTasks()
        for task in tasks:
            name, category, date, time, status = task
            identifier = f"{name}-{date}-{time}"

            if (
                date == current_date and
                time == current_time and
                status == "pending" and
                identifier not in self.notified_tasks
            ):
                notification.notify(
                    title="⏰ Task Reminder",
                    message=f"{name} ({category}) is due now!",
                    timeout=10 
                )
                self.notified_tasks.add(identifier)


def main():
    app = QApplication(sys.argv)
    window = TaskReminderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
