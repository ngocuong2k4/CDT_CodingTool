# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas",
#     "openpyxl",
#     "PyQt5",
# ]
# ///
import sys
import os
import glob
import pandas as pd
# pyrefly: ignore [missing-import]
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QAbstractItemView, QFrame, QSizePolicy, QSplitter,
    QGroupBox, QLineEdit, QStackedWidget, QFileDialog, QProgressBar
)
# pyrefly: ignore [missing-import]
from PyQt5.QtCore import Qt, QTimer, QEvent
# pyrefly: ignore [missing-import]
from PyQt5.QtGui import QFont, QIcon, QClipboard, QColor

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

class NonScrollComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def wheelEvent(self, event):
        event.ignore()

class Toast(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(46, 125, 50, 0.9);
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.hide()

    def show_toast(self, duration=1000):
        self.adjustSize()
        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 50
            self.move(x, y)
        self.show()
        self.raise_()
        QTimer.singleShot(duration, self.hide)

class ECUApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automotive ECU Coding Decoder & Encoder")
        
        # Set window icon (shows on taskbar)
        icon_path = os.path.join(get_base_dir(), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Apply modern dark styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1d23;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #8ec8f0;
                border: 1px solid #2d3340;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
                background-color: #20242c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
            }
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #b0bec5;
            }
            QLabel#title_label {
                font-size: 16px;
                font-weight: bold;
                color: #64b5f6;
                padding: 4px 0;
            }
            QTextEdit {
                font-size: 14px;
                font-family: 'Consolas', 'Courier New', monospace;
                border: 1px solid #37404f;
                border-radius: 6px;
                background-color: #272c35;
                color: #e0e0e0;
                padding: 8px;
                selection-background-color: #3a5070;
            }
            QTextEdit:focus {
                border: 1px solid #4a90d9;
            }
            QPushButton {
                background-color: #3a7bd5;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4a8be5;
            }
            QPushButton:pressed {
                background-color: #2a5baa;
            }
            QComboBox {
                font-size: 18px;
                padding: 10px 14px;
                border: 1px solid #37404f;
                border-radius: 6px;
                background-color: #272c35;
                color: #e0e0e0;
                min-width: 160px;
            }
            QComboBox:focus {
                border: 1px solid #4a90d9;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #8ec8f0;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #272c35;
                color: #e0e0e0;
                selection-background-color: #3a5070;
                border: 1px solid #37404f;
                outline: none;
            }
            QTableWidget {
                font-size: 18px;
                border: 1px solid #2d3340;
                border-radius: 6px;
                background-color: #1e222a;
                color: #e0e0e0;
                gridline-color: #2d3340;
                selection-background-color: #2a3a55;
                selection-color: #ffffff;
                outline: none;
            }
            QTableWidget::item {
                padding: 8px 10px;
                border-bottom: 1px solid #252a33;
            }
            QHeaderView::section {
                background-color: #252a33;
                color: #8ec8f0;
                font-weight: bold;
                font-size: 18px;
                border: none;
                border-right: 1px solid #2d3340;
                border-bottom: 2px solid #3a7bd5;
                padding: 12px 10px;
            }
            QSplitter::handle {
                background-color: #3a7bd5;
                width: 2px;
            }
            QScrollBar:vertical {
                background-color: #1e222a;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #37404f;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a90d9;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #1e222a;
                height: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background-color: #37404f;
                border-radius: 5px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #4a90d9;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

        self.df = None
        self.original_bytes = []
        self.current_bytes = []
        
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # === Top title bar ===
        title_bar = QHBoxLayout()
        title_bar.setSpacing(0)

        # --- Tab buttons (CDS / DTC) ---
        tab_style_active = """
            QPushButton {
                background-color: #3a7bd5;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 0px;
                padding: 6px 22px;
            }
        """
        tab_style_inactive = """
            QPushButton {
                background-color: #252a33;
                color: #8ec8f0;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 0px;
                padding: 6px 22px;
            }
            QPushButton:hover {
                background-color: #2e3644;
            }
        """
        self._tab_active_style = tab_style_active
        self._tab_inactive_style = tab_style_inactive

        self.tab_cds_btn = QPushButton("CDS")
        self.tab_cds_btn.setFixedHeight(34)
        self.tab_cds_btn.setCursor(Qt.PointingHandCursor)
        self.tab_cds_btn.setStyleSheet(tab_style_active)
        self.tab_cds_btn.clicked.connect(lambda: self.switch_tab(0))

        self.tab_dtc_btn = QPushButton("DTC")
        self.tab_dtc_btn.setFixedHeight(34)
        self.tab_dtc_btn.setCursor(Qt.PointingHandCursor)
        self.tab_dtc_btn.setStyleSheet(tab_style_inactive)
        self.tab_dtc_btn.clicked.connect(lambda: self.switch_tab(1))

        # Separator between tabs
        tab_sep = QFrame()
        tab_sep.setFrameShape(QFrame.VLine)
        tab_sep.setStyleSheet("color: #37404f;")
        tab_sep.setFixedWidth(1)

        title_bar.addWidget(self.tab_cds_btn)
        title_bar.addWidget(tab_sep)
        title_bar.addWidget(self.tab_dtc_btn)
        title_bar.addSpacing(16)

        title_bar.addStretch()
        
        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(28, 28)
        self.help_btn.setCursor(Qt.PointingHandCursor)
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8ec8f0;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #37404f;
                border-radius: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3a5070;
                border: 1px solid #4a90d9;
            }
            QPushButton:pressed {
                background-color: #2a3a55;
            }
        """)
        self.help_btn.clicked.connect(self.show_help)
        title_bar.addWidget(self.help_btn)
        
        main_layout.addLayout(title_bar)

        # === Splitter: Left 30% | Right 70% ===
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)

        # ==============================
        # LEFT PANEL (30%) - Controls
        # ==============================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(6, 6, 6, 6)

        # -- ECU Type --
        ecu_group = QGroupBox("ECU Selection")
        ecu_inner = QVBoxLayout(ecu_group)
        ecu_inner.setSpacing(6)

        ecu_row = QHBoxLayout()
        ecu_label = QLabel("ECU Type:")
        self.ecu_combo = NonScrollComboBox()
        
        script_dir = get_base_dir()
        if not script_dir:
            script_dir = "."
        odx_dir = os.path.join(script_dir, "ODX")
        search_pattern = os.path.join(odx_dir, "*_ODX.xlsx")
        ecu_files = glob.glob(search_pattern)
        ecu_types = [os.path.basename(f).replace("_ODX.xlsx", "") for f in ecu_files if not os.path.basename(f).startswith("~$")]
        
        if not ecu_types:
            self.ecu_combo.addItem("MHU")
        else:
            self.ecu_combo.addItems(sorted(ecu_types))
            
        ecu_row.addWidget(ecu_label)
        ecu_row.addWidget(self.ecu_combo, 1)
        ecu_inner.addLayout(ecu_row)
        
        left_layout.addWidget(ecu_group)

        # -- Original Coding Input --
        input_group = QGroupBox("Original Coding String (Hex)")
        input_inner = QVBoxLayout(input_group)
        input_inner.setSpacing(6)

        self.original_input = QTextEdit()
        self.original_input.setFixedHeight(90)
        self.original_input.setPlaceholderText("Paste hex string here\ne.g. AA 0B 1C 2D ...")
        input_inner.addWidget(self.original_input)

        self.decode_btn = QPushButton("▶  Decode")
        self.decode_btn.setCursor(Qt.PointingHandCursor)
        self.decode_btn.clicked.connect(self.decode_action)
        input_inner.addWidget(self.decode_btn)
        left_layout.addWidget(input_group)

        # -- Modified Coding Output --
        output_group = QGroupBox("Modified Coding String")
        output_inner = QVBoxLayout(output_group)
        output_inner.setSpacing(6)

        self.modified_output = QTextEdit()
        self.modified_output.setFixedHeight(90)
        self.modified_output.setReadOnly(True)
        self.modified_output.setStyleSheet("""
            QTextEdit {
                background-color: #1c2a1c;
                color: #66bb6a;
                font-weight: bold;
                border: 1px solid #2e4d2e;
            }
        """)
        output_inner.addWidget(self.modified_output)

        self.copy_btn = QPushButton("📋  Copy to Clipboard")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setStyleSheet("""
            QPushButton { background-color: #2e7d32; }
            QPushButton:hover { background-color: #388e3c; }
            QPushButton:pressed { background-color: #1b5e20; }
        """)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        output_inner.addWidget(self.copy_btn)
        left_layout.addWidget(output_group)

        # -- Byte Array Visual --
        byte_group = QGroupBox("Byte Array (Live View)")
        byte_inner = QVBoxLayout(byte_group)
        byte_inner.setSpacing(4)

        self.byte_display = QTextEdit()
        self.byte_display.setReadOnly(True)
        self.byte_display.setStyleSheet("""
            QTextEdit {
                font-size: 24px;
                font-family: 'Consolas', 'Courier New', monospace;
                background-color: #1a1f27;
                color: #80cbc4;
                border: 1px solid #2d3340;
            }
        """)
        byte_inner.addWidget(self.byte_display)
        left_layout.addWidget(byte_group, 1)  # stretch to fill remaining space

        # ==============================
        # RIGHT PANEL (70%) - Table
        # ==============================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(6)
        right_layout.setContentsMargins(6, 6, 6, 6)

        table_group = QGroupBox("Decoded Parameters Editor")
        table_inner = QVBoxLayout(table_group)
        table_inner.setSpacing(4)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Parameter", "BytePos (from 0)", "BitPos", "BitLength", "MethodType"
        ])
        # Column resize modes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)       # Parameter - stretch
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # BytePos
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # BitPos
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # BitLength
        header.setSectionResizeMode(4, QHeaderView.Stretch)       # MethodType (combo)

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(self.table.styleSheet() + """
            QTableWidget { alternate-background-color: #222730; }
        """)
        self.table.verticalHeader().setVisible(False)

        table_inner.addWidget(self.table)
        right_layout.addWidget(table_group, 1)

        # === Add panels to splitter ===
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 30)   # left 30%
        splitter.setStretchFactor(1, 70)   # right 70%
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        # ==============================
        # DTC PAGE
        # ==============================
        dtc_page = self.build_dtc_panel()

        # === Stacked widget to hold CDS and DTC pages ===
        self.stacked = QStackedWidget()
        self.stacked.addWidget(splitter)   # index 0 = CDS
        self.stacked.addWidget(dtc_page)   # index 1 = DTC

        main_layout.addWidget(self.stacked, 1)
        self.setCentralWidget(main_widget)
        
        self.original_input.installEventFilter(self)
        self.toast = Toast("Decoded successfully!", self)
        
    def switch_tab(self, index):
        self.stacked.setCurrentIndex(index)
        if index == 0:
            self.tab_cds_btn.setStyleSheet(self._tab_active_style)
            self.tab_dtc_btn.setStyleSheet(self._tab_inactive_style)
        else:
            self.tab_cds_btn.setStyleSheet(self._tab_inactive_style)
            self.tab_dtc_btn.setStyleSheet(self._tab_active_style)

    # ------------------------------------------------------------------
    # DTC PANEL BUILDER
    # ------------------------------------------------------------------
    def build_dtc_panel(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(8)
        layout.setContentsMargins(6, 6, 6, 6)

        # --- Input group ---
        input_group = QGroupBox("Input Excel File (Node | DTC Code)")
        input_inner = QHBoxLayout(input_group)
        input_inner.setSpacing(8)

        self.dtc_file_edit = QLineEdit()
        self.dtc_file_edit.setPlaceholderText("Select an Excel file containing Node and DTC Code columns...")
        self.dtc_file_edit.setReadOnly(True)
        self.dtc_file_edit.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                background-color: #272c35;
                color: #e0e0e0;
                border: 1px solid #37404f;
                border-radius: 6px;
                padding: 6px 10px;
            }
        """)

        self.dtc_browse_btn = QPushButton("📂  Browse")
        self.dtc_browse_btn.setCursor(Qt.PointingHandCursor)
        self.dtc_browse_btn.setFixedWidth(120)
        self.dtc_browse_btn.clicked.connect(self.dtc_browse_file)

        self.dtc_run_btn = QPushButton("▶  Lookup")
        self.dtc_run_btn.setCursor(Qt.PointingHandCursor)
        self.dtc_run_btn.setFixedWidth(120)
        self.dtc_run_btn.clicked.connect(self.dtc_run_lookup)

        input_inner.addWidget(self.dtc_file_edit, 1)
        input_inner.addWidget(self.dtc_browse_btn)
        input_inner.addWidget(self.dtc_run_btn)
        layout.addWidget(input_group)

        # --- Status bar ---
        self.dtc_status_label = QLabel("No data loaded. Please select an Excel file and click Lookup.")
        self.dtc_status_label.setStyleSheet("color: #78909c; font-size: 12px; font-weight: normal;")
        layout.addWidget(self.dtc_status_label)

        # --- Result table ---
        result_group = QGroupBox("DTC Lookup Results")
        result_inner = QVBoxLayout(result_group)
        result_inner.setSpacing(4)

        # Export button row
        export_row = QHBoxLayout()
        export_row.addStretch()
        self.dtc_export_btn = QPushButton("💾  Export to Excel")
        self.dtc_export_btn.setCursor(Qt.PointingHandCursor)
        self.dtc_export_btn.setEnabled(False)
        self.dtc_export_btn.setStyleSheet("""
            QPushButton { background-color: #2e7d32; }
            QPushButton:hover { background-color: #388e3c; }
            QPushButton:pressed { background-color: #1b5e20; }
            QPushButton:disabled { background-color: #37404f; color: #607d8b; }
        """)
        self.dtc_export_btn.clicked.connect(self.dtc_export_results)
        export_row.addWidget(self.dtc_export_btn)
        result_inner.addLayout(export_row)

        self.dtc_table = QTableWidget(0, 3)
        self.dtc_table.setHorizontalHeaderLabels(["Node", "DTC Code", "DTC Name"])
        dtc_header = self.dtc_table.horizontalHeader()
        dtc_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        dtc_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        dtc_header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.dtc_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dtc_table.setAlternatingRowColors(True)
        self.dtc_table.setStyleSheet(self.dtc_table.styleSheet() + """
            QTableWidget { alternate-background-color: #222730; }
        """)
        self.dtc_table.verticalHeader().setVisible(False)
        self.dtc_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        result_inner.addWidget(self.dtc_table)
        layout.addWidget(result_group, 1)

        return page

    # ------------------------------------------------------------------
    # DTC LOGIC
    # ------------------------------------------------------------------
    def dtc_browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Input Excel File", "",
            "Excel Files (*.xlsx *.xls)"
        )
        if path:
            self.dtc_file_edit.setText(path)

    @staticmethod
    def _norm(s):
        """Normalize a string: lowercase, strip spaces/underscores for column matching."""
        return str(s).strip().lower().replace(" ", "").replace("_", "")

    def dtc_find_col(self, columns, *keywords):
        """Find the first column whose normalized name contains ANY of the given keywords."""
        for col in columns:
            n = self._norm(col)
            if any(kw in n for kw in keywords):
                return col
        return None

    def dtc_find_col_no_hex(self, columns, *keywords):
        """
        Like dtc_find_col but PREFERS columns that do NOT contain 'hex' in their name.
        First pass: match keyword AND no 'hex'.
        Second pass (fallback): match keyword regardless of 'hex'.
        This ensures 'DTC Number' is chosen over 'DTC Number (hex)'.
        """
        # Pass 1: match keyword, exclude 'hex'
        for col in columns:
            n = self._norm(col)
            if any(kw in n for kw in keywords) and 'hex' not in n:
                return col
        # Pass 2: fallback – accept even if it has 'hex'
        for col in columns:
            n = self._norm(col)
            if any(kw in n for kw in keywords):
                return col
        return None

    def dtc_load_odx_dtc_map(self):
        """
        Scan all *_ODX.xlsx files and build a lookup dict:
          { normalized_dtc_number (str) : dtc_name (str) }
        Searches every sheet whose name contains 'dtc'.
        """
        dtc_map = {}  # key: norm dtc number, value: dtc name
        script_dir = get_base_dir()
        odx_dir = os.path.join(script_dir, "ODX")
        odx_files = glob.glob(os.path.join(odx_dir, "*_ODX.xlsx"))
        odx_files = [f for f in odx_files if not os.path.basename(f).startswith("~$")]

        for f in odx_files:
            try:
                xls = pd.ExcelFile(f)
            except Exception:
                continue

            dtc_sheets = [s for s in xls.sheet_names if 'dtc' in self._norm(s)]

            for sheet in dtc_sheets:
                try:
                    df = pd.read_excel(xls, sheet_name=sheet, header=None)
                except Exception:
                    continue

                # Find header row (must have DTC Number and DTC Name)
                hdr_idx = -1
                for idx, row in df.iterrows():
                    row_vals = [str(v) for v in row.values if pd.notna(v)]
                    norms = [self._norm(v) for v in row_vals]
                    has_number = any('dtcnumber' in n or 'dtccode' in n for n in norms)
                    has_name   = any('dtcname' in n or 'faultname' in n or 'description' in n for n in norms)
                    if has_number:
                        hdr_idx = idx
                        break

                if hdr_idx == -1:
                    # Fallback: just use row 0 as header
                    hdr_idx = 0

                try:
                    df2 = pd.read_excel(xls, sheet_name=sheet, header=hdr_idx)
                except Exception:
                    continue

                col_number = self.dtc_find_col_no_hex(df2.columns, 'dtcnumber', 'dtccode', 'dtc_number', 'dtc_code')
                col_name   = self.dtc_find_col(df2.columns, 'dtcname', 'faultname', 'description', 'name')

                if col_number is None:
                    continue

                for _, row in df2.iterrows():
                    raw_num = row[col_number]
                    if pd.isna(raw_num):
                        continue
                    key = self._norm(str(raw_num))
                    if not key:
                        continue

                    name_val = ""
                    if col_name is not None and not pd.isna(row.get(col_name, None)):
                        name_val = str(row[col_name]).strip()

                    if key not in dtc_map:
                        dtc_map[key] = name_val

        return dtc_map

    def dtc_run_lookup(self):
        input_path = self.dtc_file_edit.text().strip()
        if not input_path or not os.path.exists(input_path):
            QMessageBox.warning(self, "Warning", "Please select a valid input Excel file.")
            return

        self.dtc_run_btn.setEnabled(False)
        self.dtc_run_btn.setText("⏳ Loading...")
        self.dtc_status_label.setText("Reading input file...")
        QApplication.processEvents()

        try:
            # ----------------------------------------------------------------
            # Step 1: Read input file – scan ALL rows across ALL sheets
            #         to find the real header row containing Node & DTC Code
            # ----------------------------------------------------------------
            in_xls = pd.ExcelFile(input_path)
            in_df = None
            col_node = None
            col_dtc = None
            found_sheet = None

            for sheet_name in in_xls.sheet_names:
                try:
                    raw_df = pd.read_excel(in_xls, sheet_name=sheet_name, header=None)
                except Exception:
                    continue

                hdr_idx = -1
                for idx, row in raw_df.iterrows():
                    row_vals = [str(v) for v in row.values if pd.notna(v)]
                    norms = [self._norm(v) for v in row_vals]
                    has_node = any('node' in n or 'ecu' in n for n in norms)
                    has_dtc  = any('dtc' in n or 'code' in n or 'fault' in n for n in norms)
                    if has_node and has_dtc:
                        hdr_idx = idx
                        break

                if hdr_idx == -1:
                    # Fallback: accept row with at least one matching keyword
                    for idx, row in raw_df.iterrows():
                        row_vals = [str(v) for v in row.values if pd.notna(v)]
                        norms = [self._norm(v) for v in row_vals]
                        has_node = any('node' in n or 'ecu' in n for n in norms)
                        has_dtc  = any('dtc' in n or 'code' in n or 'fault' in n for n in norms)
                        if has_node or has_dtc:
                            hdr_idx = idx
                            break

                if hdr_idx == -1:
                    hdr_idx = 0  # last resort

                try:
                    candidate_df = pd.read_excel(in_xls, sheet_name=sheet_name, header=hdr_idx)
                except Exception:
                    continue

                # Try to find Node and DTC columns in ALL columns of this sheet
                cand_node = self.dtc_find_col(candidate_df.columns, 'node', 'ecu', 'ecuname')
                cand_dtc  = self.dtc_find_col(candidate_df.columns, 'dtccode', 'dtc', 'code', 'faultcode', 'fault')

                if cand_node is not None and cand_dtc is not None:
                    in_df = candidate_df
                    col_node = cand_node
                    col_dtc = cand_dtc
                    found_sheet = sheet_name
                    break  # found a good sheet

            if in_df is None or col_node is None or col_dtc is None:
                all_sheets_info = []
                for sn in in_xls.sheet_names:
                    try:
                        tmp = pd.read_excel(in_xls, sheet_name=sn, header=None)
                        cols = list(tmp.iloc[0].dropna().values)
                        all_sheets_info.append(f"  Sheet '{sn}': {cols}")
                    except Exception:
                        all_sheets_info.append(f"  Sheet '{sn}': (read error)")
                QMessageBox.critical(self, "Error",
                    f"Could not find Node and DTC Code columns in any sheet of the input file.\n\n"
                    f"First row of each sheet:\n" + "\n".join(all_sheets_info))
                return

            self.dtc_status_label.setText(f"Reading input from sheet '{found_sheet}' — Scanning ODX files...")
            QApplication.processEvents()

            # ----------------------------------------------------------------
            # Step 2: Load DTC map from all ODX files
            # ----------------------------------------------------------------
            dtc_map = self.dtc_load_odx_dtc_map()

            if not dtc_map:
                QMessageBox.warning(self, "Warning",
                    "No DTC data found in ODX files.\n"
                    "Check the ODX folder and ensure files contain a sheet with 'DTC' in its name.")
                return

            self.dtc_status_label.setText("Looking up DTC Names...")
            QApplication.processEvents()

            # ----------------------------------------------------------------
            # Step 3: Build result rows – skip entirely empty/NaN rows
            # ----------------------------------------------------------------
            results = []
            not_found = 0
            for _, row in in_df.iterrows():
                node_raw = row[col_node]
                dtc_raw_val = row[col_dtc]
                # Skip rows where both are empty/NaN
                if pd.isna(node_raw) and pd.isna(dtc_raw_val):
                    continue
                node_val = str(node_raw).strip() if not pd.isna(node_raw) else ""
                dtc_raw  = str(dtc_raw_val).strip()  if not pd.isna(dtc_raw_val) else ""
                dtc_key  = self._norm(dtc_raw)
                dtc_name = dtc_map.get(dtc_key, "")
                if not dtc_name:
                    not_found += 1
                results.append((node_val, dtc_raw, dtc_name))

            # Populate table
            self.dtc_table.setRowCount(0)
            for node_val, dtc_code, dtc_name in results:
                r = self.dtc_table.rowCount()
                self.dtc_table.insertRow(r)

                item_node = QTableWidgetItem(node_val)
                item_dtc  = QTableWidgetItem(dtc_code)
                item_name = QTableWidgetItem(dtc_name)

                # Highlight rows where DTC Name not found
                if not dtc_name:
                    warn_color = QColor("#4a2020")
                    item_node.setBackground(warn_color)
                    item_dtc.setBackground(warn_color)
                    item_name.setBackground(warn_color)
                    item_name.setText("⚠ Not Found")
                    item_name.setForeground(QColor("#ef9a9a"))

                self.dtc_table.setItem(r, 0, item_node)
                self.dtc_table.setItem(r, 1, item_dtc)
                self.dtc_table.setItem(r, 2, item_name)

            found = len(results) - not_found
            self.dtc_status_label.setText(
                f"✅ Done: {len(results)} row(s) — Found: {found} — Not found: {not_found}"
            )
            self.dtc_status_label.setStyleSheet("color: #66bb6a; font-size: 12px; font-weight: bold;")
            self.dtc_export_btn.setEnabled(True)

            # Store results for export
            self._dtc_results = results

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during lookup:\n{str(e)}")
            self.dtc_status_label.setText("❌ An error occurred.")
            self.dtc_status_label.setStyleSheet("color: #ef5350; font-size: 12px; font-weight: bold;")
        finally:
            self.dtc_run_btn.setEnabled(True)
            self.dtc_run_btn.setText("▶  Lookup")

    def dtc_export_results(self):
        if not hasattr(self, '_dtc_results') or not self._dtc_results:
            QMessageBox.warning(self, "Warning", "No data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "DTC_Lookup_Result.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return

        try:
            out_df = pd.DataFrame(self._dtc_results, columns=["Node", "DTC Code", "DTC Name"])
            out_df.to_excel(path, index=False)
            QMessageBox.information(self, "Success", f"File exported successfully:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting file:\n{str(e)}")

    def eventFilter(self, obj, event):
        if obj == self.original_input and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.decode_btn.animateClick()
                return True
        return super().eventFilter(obj, event)
        
    def load_excel(self, ecu_type):
        script_dir = get_base_dir()
        if not script_dir:
            script_dir = "."
        filename = os.path.join(script_dir, "ODX", f"{ecu_type}_ODX.xlsx")
        try:
            xls = pd.ExcelFile(filename)
            target_sheet = xls.sheet_names[0]  # Default to first sheet
            
            def normalize_name(s):
                return s.lower().replace(" ", "").replace("_", "")
                
            sheet_cds_f108 = [s for s in xls.sheet_names if 'cdscodingf108' in normalize_name(s)]
            sheet_cdscoding = [s for s in xls.sheet_names if 'cdscoding' in normalize_name(s)]
            sheet_coding_f108 = [s for s in xls.sheet_names if 'codingf108' in normalize_name(s)]
            sheet_cds = [s for s in xls.sheet_names if 'cds' in normalize_name(s)]
            sheet_coding = [s for s in xls.sheet_names if 'coding' in normalize_name(s)]
            
            if sheet_cds_f108:
                target_sheet = sheet_cds_f108[0]
            elif sheet_cdscoding:
                target_sheet = sheet_cdscoding[0]
            elif sheet_coding_f108:
                target_sheet = sheet_coding_f108[0]
            elif sheet_cds:
                target_sheet = sheet_cds[0]
            elif sheet_coding:
                target_sheet = sheet_coding[0]
                    
            # Read without headers first to find the correct header row
            temp_df = pd.read_excel(xls, sheet_name=target_sheet, header=None)
            header_idx = -1
            for idx, row in temp_df.iterrows():
                row_vals = [str(v).strip().lower() for v in row.values if pd.notna(v)]
                
                has_param = any('parameter' in v for v in row_vals)
                has_bitpos = any('bitpos' in v.replace(' ', '') for v in row_vals)
                
                if has_param and has_bitpos:
                    header_idx = idx
                    break
            
            if header_idx == -1:
                raise ValueError(f"Could not find a valid header row containing 'Parameter' and 'BitPos' in sheet '{target_sheet}' of {filename}")
                
            self.df = pd.read_excel(xls, sheet_name=target_sheet, header=header_idx)
            
            # Map columns to their lowercase versions to handle case insensitivity
            col_map = {str(c).strip().lower(): c for c in self.df.columns}
            
            self.actual_cols = {}
            self.actual_cols['parameter'] = next((col_map[c] for c in col_map if 'parameter' in c), None)
            self.actual_cols['bytepos'] = next((col_map[c] for c in col_map if 'bytepos' in c.replace(' ', '')), None)
            self.actual_cols['bitpos'] = next((col_map[c] for c in col_map if 'bitpos' in c.replace(' ', '')), None)
            self.actual_cols['bitlength'] = next((col_map[c] for c in col_map if 'bitlength' in c.replace(' ', '') or 'bit len' in c), None)
            self.actual_cols['methodtype'] = next((col_map[c] for c in col_map if 'method' in c), None)
            
            missing = [k for k, v in self.actual_cols.items() if v is None]
            if missing:
                raise ValueError(f"Missing required column(s): {', '.join(missing)} in sheet '{target_sheet}' (Row {header_idx + 1})")
                
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"Excel file '{filename}' not found in the current directory.")
            self.df = None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading Excel file:\n{str(e)}")
            self.df = None
            
    def parse_method_type(self, method_str):
        mapping = {}
        reverse_mapping = {}
        if pd.isna(method_str):
            return mapping, reverse_mapping
            
        lines = str(method_str).split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.lower().startswith('type='):
                continue
            parts = line.split('=', 1)
            if len(parts) == 2:
                try:
                    val_str = parts[0].strip()
                    val = int(val_str, 16) if val_str.lower().startswith('0x') else int(val_str)
                    label = parts[1].strip()
                    mapping[val] = label
                    reverse_mapping[label] = val
                except ValueError:
                    continue
        return mapping, reverse_mapping

    def parse_hex_string(self, hex_str):
        hex_str = hex_str.strip().replace('\n', ' ')
        parts = hex_str.split()
        bytes_list = []
        for p in parts:
            try:
                bytes_list.append(int(p, 16))
            except ValueError:
                raise ValueError(f"Invalid hex byte found: '{p}'")
        return bytes_list
        
    def decode_action(self):
        hex_str = self.original_input.toPlainText()
        if not hex_str:
            QMessageBox.warning(self, "Warning", "Please enter a coding string first.")
            return

        original_btn_text = self.decode_btn.text()
        self.decode_btn.setText("⏳ Decoding...")
        self.decode_btn.setEnabled(False)
        QApplication.processEvents()

        ecu_type = self.ecu_combo.currentText()
        self.load_excel(ecu_type)
        if self.df is None:
            self.decode_btn.setText(original_btn_text)
            self.decode_btn.setEnabled(True)
            return
            
        try:
            self.original_bytes = self.parse_hex_string(hex_str)
            self.current_bytes = list(self.original_bytes)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error parsing hex string:\n{str(e)}")
            self.decode_btn.setText(original_btn_text)
            self.decode_btn.setEnabled(True)
            return
            
        self.table.setRowCount(0)
        
        for index, row in self.df.iterrows():
            param = str(row[self.actual_cols['parameter']])
            try:
                byte_pos = int(row[self.actual_cols['bytepos']])
                bit_pos = int(row[self.actual_cols['bitpos']])
                bit_len = int(row[self.actual_cols['bitlength']])
            except ValueError:
                continue # Skip invalid rows
                
            # If the parameter is "Short VIN", ignore the 'H' byte if it's included in the length
            if "short vin" in param.lower() and byte_pos == 5 and bit_len == 56:
                byte_pos = 6
                bit_len = 48
                
            method_str = row[self.actual_cols['methodtype']]
            input_idx = byte_pos - 3
            
            if input_idx < 0 or input_idx >= len(self.current_bytes):
                val_int = None
            else:
                byte_val = self.current_bytes[input_idx]
                shifted = byte_val >> bit_pos
                mask = (1 << bit_len) - 1
                val_int = shifted & mask
                
            mapping, reverse_mapping = self.parse_method_type(method_str)
            
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            # Column 0: Parameter
            item_param = QTableWidgetItem(param)
            item_param.setFlags(item_param.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 0, item_param)
            
            # Column 1: BytePos (from 0)
            item_bytepos = QTableWidgetItem(str(byte_pos))
            item_bytepos.setFlags(item_bytepos.flags() & ~Qt.ItemIsEditable)
            item_bytepos.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item_bytepos)
            
            # Column 2: BitPos
            item_bitpos = QTableWidgetItem(str(bit_pos))
            item_bitpos.setFlags(item_bitpos.flags() & ~Qt.ItemIsEditable)
            item_bitpos.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, item_bitpos)
            
            # Column 3: BitLength
            item_bitlen = QTableWidgetItem(str(bit_len))
            item_bitlen.setFlags(item_bitlen.flags() & ~Qt.ItemIsEditable)
            item_bitlen.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, item_bitlen)
            
            # Column 4: MethodType (ComboBox or LineEdit)
            is_multi_byte = bit_len >= 8 and (bit_len % 8 == 0) and bit_pos == 0 and ("vin" in param.lower() or "seri" in param.lower() or "name" in param.lower())
            
            if is_multi_byte:
                num_bytes = bit_len // 8
                if input_idx < 0 or input_idx + num_bytes > len(self.current_bytes):
                    val_bytes = None
                else:
                    val_bytes = self.current_bytes[input_idx : input_idx + num_bytes]
                    
                line_edit = QLineEdit()
                line_edit.setStyleSheet("""
                    QLineEdit {
                        border: none;
                        background-color: transparent;
                        color: #e0e0e0;
                        font-size: 18px;
                        padding: 6px 10px;
                    }
                """)
                if val_bytes is None:
                    line_edit.setText("Error: Out of bounds")
                    line_edit.setReadOnly(True)
                else:
                    ascii_str = "".join([chr(b) if 32 <= b <= 126 else "?" for b in val_bytes])
                    line_edit.setText(ascii_str)
                    line_edit.editingFinished.connect(
                        lambda r=row_idx, b_pos=byte_pos, b_len=bit_len, le=line_edit:
                        self.on_multibyte_changed(r, b_pos, b_len, le)
                    )
                self.table.setCellWidget(row_idx, 4, line_edit)
            else:
                combo = NonScrollComboBox()
                combo.setStyleSheet("""
                    QComboBox {
                        border: none;
                        background-color: transparent;
                        color: #e0e0e0;
                        font-size: 18px;
                        padding: 6px 10px;
                    }
                    QComboBox::drop-down { border: none; width: 20px; }
                    QComboBox::down-arrow {
                        border-left: 4px solid transparent;
                        border-right: 4px solid transparent;
                        border-top: 5px solid #8ec8f0;
                    }
                    QComboBox QAbstractItemView {
                        background-color: #272c35;
                        color: #e0e0e0;
                        selection-background-color: #3a5070;
                        border: 1px solid #37404f;
                    }
                """)
                
                if val_int is None:
                    combo.addItem("Error: Byte out of bounds")
                    combo.setEnabled(False)
                else:
                    for lbl, v in reverse_mapping.items():
                        combo.addItem(f"0x{v:X} - {lbl}", userData=v)
                        
                    if val_int not in mapping:
                        unknown_lbl = f"Unknown (0x{val_int:X})"
                        combo.addItem(unknown_lbl, userData=val_int)
                        combo.setCurrentText(unknown_lbl)
                    else:
                        combo.setCurrentText(f"0x{val_int:X} - {mapping[val_int]}")
                        
                    combo.currentIndexChanged.connect(
                        lambda idx, r=row_idx, b_pos=byte_pos, b_bit=bit_pos, b_len=bit_len, cb=combo: 
                        self.on_value_changed(r, b_pos, b_bit, b_len, cb)
                    )
                    
                self.table.setCellWidget(row_idx, 4, combo)
            
        self.update_modified_output()
        self.update_byte_display()
        self.toast.show_toast(3000)
        self.decode_btn.setText(original_btn_text)
        self.decode_btn.setEnabled(True)
        
    def on_value_changed(self, row_idx, byte_pos, bit_pos, bit_len, combo):
        input_idx = byte_pos - 3
        if input_idx < 0 or input_idx >= len(self.current_bytes):
            return
            
        new_val = combo.currentData()
        if new_val is None:
            return
            
        byte_val = self.current_bytes[input_idx]
        mask = (1 << bit_len) - 1
        
        # Clear old bits using negated mask
        byte_val = byte_val & ~(mask << bit_pos)
        # Apply new bits using bitwise OR
        byte_val = byte_val | ((new_val & mask) << bit_pos)
        
        self.current_bytes[input_idx] = byte_val
        self.update_modified_output()
        self.update_byte_display()
        
    def on_multibyte_changed(self, row_idx, byte_pos, bit_len, line_edit):
        input_idx = byte_pos - 3
        num_bytes = bit_len // 8
        if input_idx < 0 or input_idx + num_bytes > len(self.current_bytes):
            return
            
        new_text = line_edit.text()
        
        # Pad or truncate new text
        if len(new_text) < num_bytes:
            new_text = new_text.ljust(num_bytes, ' ')
        elif len(new_text) > num_bytes:
            new_text = new_text[:num_bytes]
            
        for i in range(num_bytes):
            self.current_bytes[input_idx + i] = ord(new_text[i])
            
        self.update_modified_output()
        self.update_byte_display()
        
    def update_modified_output(self):
        if len(self.current_bytes) > 0:
            # Calculate CRC-8 SAE J1850 starting from byte 12.
            # Since the input string starts at byte 3, byte 12 corresponds to index 9.
            data_to_crc = self.current_bytes[9:-1]
            crc = 0xFF
            for byte in data_to_crc:
                crc ^= byte
                for _ in range(8):
                    if crc & 0x80:
                        crc = (crc << 1) ^ 0x1D
                    else:
                        crc <<= 1
                    crc &= 0xFF
            new_crc = crc ^ 0xFF
            
            # Update the last byte with the new CRC
            self.current_bytes[-1] = new_crc

        hex_strs = [f"{b:02X}" for b in self.current_bytes]
        self.modified_output.setPlainText(" ".join(hex_strs))

    def update_byte_display(self):
        """Update the byte array visual display with index and hex values."""
        if not self.current_bytes:
            self.byte_display.setPlainText("")
            return

        lines = []
        lines.append(f"Total: {len(self.current_bytes)} bytes")
        lines.append("─" * 34)
        lines.append(f"{'Idx':<5} {'Hex':<6} {'Dec':<5} {'Binary'}")
        lines.append("─" * 34)

        for i, b in enumerate(self.current_bytes):
            # Highlight changed bytes vs original
            marker = " "
            if i < len(self.original_bytes) and b != self.original_bytes[i]:
                marker = "◆"
                
            lines.append(f" {i:<4} 0x{b:02X}   {b:<5} {b:08b} {marker}")

        lines.append("─" * 34)
        # Show diff summary
        changed = sum(1 for i, b in enumerate(self.current_bytes)
                      if i < len(self.original_bytes) and b != self.original_bytes[i])
        if changed:
            lines.append(f"◆ {changed} byte(s) modified")

        self.byte_display.setPlainText("\n".join(lines))

    def copy_to_clipboard(self):
        cb = QApplication.clipboard()
        cb.setText(self.modified_output.toPlainText())
        self.copy_btn.setText("✅  Copied!")
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋  Copy to Clipboard"))

    def show_help(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Help / Feedback")
        msg.setText("For any feedback or bug reports, please contact: cuongnx11")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1d23;
                color: #e0e0e0;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3a7bd5;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #4a8be5;
            }
            QPushButton:pressed {
                background-color: #2a5baa;
            }
        """)
        msg.exec_()

if __name__ == "__main__":
    # Set AppUserModelID to ensure taskbar icon displays correctly on Windows
    import ctypes
    try:
        myappid = 'automotive.ecu.decoder.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    
    # Set the application icon
    base_dir = get_base_dir()
    icon_path = os.path.join(base_dir, "icon.png")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(base_dir, "icon.ico")
        
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    window = ECUApp()
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
        
    window.showMaximized()
    sys.exit(app.exec_())
