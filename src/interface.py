from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QFileDialog, \
    QHBoxLayout, QDialog, QLabel

from src.drawing import ENVELOPE_DETAIL_LINE_LAYER, EXTERIOR_WALLS_LAYER_HATCH_DEFAULT, FILLED_REGION_LAYER_DEFAULT, \
    get_net_area


class NetArea_QDialog(QDialog):
    def __init__(self, result: float):
        super().__init__()
        self.setWindowTitle("Net Area")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Net Area:"))

        # horizontal layout for result and copy button
        result_layout = QHBoxLayout()
        result_box = QLineEdit(f"{result:.3f}")
        result_box.setReadOnly(True)
        result_layout.addWidget(result_box)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(lambda: QGuiApplication.clipboard().setText(result_box.text()))
        result_layout.addWidget(copy_button)

        layout.addLayout(result_layout)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)


class Main_MainWindow(QMainWindow):
    __exterior_walls_layer_QLineEdit: QLineEdit
    __exterior_walls_layer_hatch_QLineEdit: QLineEdit
    __filled_region_layer_QLineEdit: QLineEdit

    __filename_QLineEdit: QLineEdit
    __browse_QPushButton: QPushButton

    __run_QPushButton: QPushButton

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Net Area")

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        form = QFormLayout()
        main_layout.addLayout(form)

        # text inputs
        self.__exterior_walls_layer_QLineEdit = QLineEdit(ENVELOPE_DETAIL_LINE_LAYER)
        self.__exterior_walls_layer_hatch_QLineEdit = QLineEdit(EXTERIOR_WALLS_LAYER_HATCH_DEFAULT)
        self.__filled_region_layer_QLineEdit = QLineEdit(FILLED_REGION_LAYER_DEFAULT)

        form.addRow("Envelope detail line layer", self.__exterior_walls_layer_QLineEdit)
        form.addRow("Exterior walls hatch", self.__exterior_walls_layer_hatch_QLineEdit)
        form.addRow("Filled region layer", self.__filled_region_layer_QLineEdit)

        file_layout = QHBoxLayout()
        self.__filename_QLineEdit = QLineEdit()
        self.__browse_QPushButton = QPushButton("Browse")
        file_layout.addWidget(self.__filename_QLineEdit)
        file_layout.addWidget(self.__browse_QPushButton)
        form.addRow("Filename:", file_layout)

        # run button
        self.__run_QPushButton = QPushButton("RUN")
        form.addRow("", self.__run_QPushButton)

        self.__browse_QPushButton.clicked.connect(self.browse_QPushButton_SLOT)
        self.__run_QPushButton.clicked.connect(self.run_QPushButton_SLOT)

        self.setFixedWidth(768)

    def browse_QPushButton_SLOT(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File", "", "DXF Files (*.dxf)")
        if file:
            self.__filename_QLineEdit.setText(file)

    def run_QPushButton_SLOT(self):
        if self.__filename_QLineEdit.text() != "":
            try:
                net_area_ = get_net_area(self.__filename_QLineEdit.text())

                net_area_QDialog = NetArea_QDialog(net_area_)
                net_area_QDialog.exec()
            except Exception as e:
                print("ERROR: I/O")
        else:
            print("ERROR: EMPTY FILENAME")
