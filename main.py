import json
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QGridLayout, QLabel, QHBoxLayout, QVBoxLayout,
    QLineEdit, QScrollArea, QFileDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer

from font_7x4 import get_char_bitmap  # твой ASCII-шрифт 4x7

SIZE = 16
PIXELS = SIZE * SIZE

def build_text_columns(text: str):
    columns = []
    for idx, ch in enumerate(text):
        bmp = get_char_bitmap(ch)
        for x in range(4):
            col = []
            for y in range(7):
                col.append(1 if bmp[y][x] else 0)
            columns.append(col)
        if idx != len(text) - 1:
            columns.append([0] * 7)
    return columns

# ===================== ПИКСЕЛЬ =====================
class PixelLabel(QLabel):
    def __init__(self, x, y, matrix):
        super().__init__("○")
        self.x = x
        self.y = y
        self.matrix = matrix
        self.on = False
        self.setFixedSize(28, 28)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 20))
        self.setStyleSheet("border: 1px solid #777; color: #555;")

    def set_on(self, state, mark_modified=True):
        self.on = state
        if self.on:
            self.setStyleSheet("border: 1px solid #777; color: red;")
            self.setText("●")
        else:
            self.setStyleSheet("border: 1px solid #777; color: #555;")
            self.setText("○")
        if mark_modified:
            self.matrix.editor.mark_modified()

    def mousePressEvent(self, event):
        if not self.matrix.editor.session_active:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_on(True)
        elif event.button() == Qt.MouseButton.RightButton:
            self.set_on(False)

    def mouseMoveEvent(self, event):
        if not self.matrix.editor.session_active:
            return
        if event.buttons() & Qt.MouseButton.LeftButton:
            if not self.on:
                self.set_on(True)
        if event.buttons() & Qt.MouseButton.RightButton:
            if self.on:
                self.set_on(False)

# ===================== МАТРИЦА 16×16 =====================
class Matrix(QWidget):
    def __init__(self, name, editor):
        super().__init__()
        self.name = name
        self.editor = editor
        layout = QVBoxLayout()
        layout.addWidget(QLabel(name))
        grid = QGridLayout()
        self.pixels = []
        for y in range(SIZE):
            row = []
            for x in range(SIZE):
                px = PixelLabel(x, y, self)
                row.append(px)
                grid.addWidget(px, y, x)
            self.pixels.append(row)
        layout.addLayout(grid)
        self.setLayout(layout)

    def get_frame(self):
        return [1 if self.pixels[y][x].on else 0 for y in range(SIZE) for x in range(SIZE)]

    def load_frame(self, frame):
        for i in range(PIXELS):
            x = i % SIZE
            y = i // SIZE
            self.pixels[y][x].set_on(frame[i], mark_modified=False)

    def clear(self):
        for y in range(SIZE):
            for x in range(SIZE):
                self.pixels[y][x].set_on(False)

# ===================== ГАЛЕРЕЯ =====================
class FramesGallery(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setWindowTitle("Галерея кадров")
        self.resize(800, 600)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.scroll.setWidget(self.container)
        main = QVBoxLayout(self)
        main.addWidget(self.scroll)

    def refresh(self):
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        for index, frame in enumerate(self.editor.frames):
            title = QLabel(f"Кадр {index + 1}")
            title.setStyleSheet("font-weight: bold;")
            self.layout.addWidget(title)

            left = frame["left"]
            right = frame["right"]
            text = ""
            for y in range(SIZE):
                l = "".join("●" if left[y*SIZE+x] else "○" for x in range(SIZE))
                r = "".join("●" if right[y*SIZE+x] else "○" for x in range(SIZE))
                text += f"{l}   {r}\n"

            label = QLabel(text)
            label.setFont(QFont("Consolas", 10))
            label.mousePressEvent = lambda e, i=index: self.editor.load_frame_direct(i)
            self.layout.addWidget(label)

# ===================== РЕДАКТОР КАДРА =====================
class FrameEditGallery(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setWindowTitle("Редактирование кадров")
        self.resize(600, 400)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.scroll.setWidget(self.container)
        main = QVBoxLayout(self)
        main.addWidget(self.scroll)

        self.save_btn = QPushButton("Сохранить изменения кадра")
        self.save_btn.clicked.connect(self.save_current_frame)
        main.addWidget(self.save_btn)

        self.current_index = None

    def refresh(self):
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        for index, frame in enumerate(self.editor.frames):
            title = QLabel(f"Кадр {index + 1}")
            title.setStyleSheet("font-weight: bold;")
            self.layout.addWidget(title)

            left = frame["left"]
            right = frame["right"]
            text = ""
            for y in range(SIZE):
                l = "".join("●" if left[y*SIZE+x] else "○" for x in range(SIZE))
                r = "".join("●" if right[y*SIZE+x] else "○" for x in range(SIZE))
                text += f"{l}   {r}\n"

            label = QLabel(text)
            label.setFont(QFont("Consolas", 10))
            label.setStyleSheet("border: 1px solid #333;")
            label.mousePressEvent = lambda e, i=index: self.load_frame_to_editor(i)
            self.layout.addWidget(label)

    def load_frame_to_editor(self, index):
        self.current_index = index
        self.editor.load_frame_direct(index)

    def save_current_frame(self):
        if self.current_index is None:
            return
        self.editor.save_frame_changes()
        self.editor.modified = True
        print(f"Кадр {self.current_index + 1} сохранен!")

# ===================== ГЛАВНОЕ ОКНО =====================
class EyesEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор глаз с сессиями")
        self.frames = []
        self.current_frame_index = None
        self.anim_index = 0
        self.anim_playing = False
        self.gallery = None
        self.edit_gallery = None
        self.session_active = False
        self.session_file = None
        self.modified = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.play_step)

        layout = QVBoxLayout(self)

        # Имя сессии
        self.file_name_edit = QLineEdit()
        self.file_name_edit.setPlaceholderText("Введите имя файла для новой сессии")
        layout.addWidget(self.file_name_edit)

        # FPS
        row_fps = QHBoxLayout()
        row_fps.addWidget(QLabel("FPS:"))
        self.fps_input = QLineEdit()
        self.fps_input.setFixedWidth(50)
        self.fps_input.setText("12")
        self.fps_input.textChanged.connect(lambda _: self.mark_modified())
        row_fps.addWidget(self.fps_input)
        layout.addLayout(row_fps)

        # Кнопки сессии
        sesh_layout = QHBoxLayout()
        self.new_session_btn = QPushButton("Новая сессия")
        self.end_session_btn = QPushButton("Завершить сессию")
        self.new_session_btn.clicked.connect(self.start_session)
        self.end_session_btn.clicked.connect(self.end_session)
        sesh_layout.addWidget(self.new_session_btn)
        sesh_layout.addWidget(self.end_session_btn)
        layout.addLayout(sesh_layout)

        # Бегущая строка
        row_text = QHBoxLayout()
        row_text.addWidget(QLabel("Текст:"))
        self.text_input = QLineEdit()
        row_text.addWidget(self.text_input)
        gen_btn = QPushButton("Создать бегущую строку")
        gen_btn.clicked.connect(self.generate_scrolling_text)
        row_text.addWidget(gen_btn)
        layout.addLayout(row_text)

        # Матрицы
        row = QHBoxLayout()
        self.left_matrix = Matrix("LEFT", self)
        self.right_matrix = Matrix("RIGHT", self)
        row.addWidget(self.left_matrix)
        row.addWidget(self.right_matrix)
        layout.addLayout(row)

        # Кнопки управления кадрами
        btns = QHBoxLayout()
        for text, fn in [
            ("Добавить кадр", self.add_frame),
            ("Сохранить JSON", self.save_json),
            ("Загрузить JSON", self.load_json),
            ("▶ Старт", self.start_animation),
            ("■ Стоп", self.stop_animation),
            ("Сохранить изменения", self.save_changes_to_file),
            ("Галерея", self.open_gallery),
            ("Очистить матрицу", self.clear_all),
            ("Изменить кадр", self.edit_frame),
        ]:
            b = QPushButton(text)
            b.clicked.connect(fn)
            btns.addWidget(b)
        layout.addLayout(btns)

    # ===== Вспомогательные =====
    def mark_modified(self):
        if self.session_file:
            self.modified = True

    # ===== Сессии =====
    def start_session(self):
        name = self.file_name_edit.text().strip()
        if not name:
            return
        self.session_file = name
        self.session_active = True
        self.frames.clear()
        self.left_matrix.clear()
        self.right_matrix.clear()
        self.modified = True

    def end_session(self):
        self.session_active = False
        self.left_matrix.clear()
        self.right_matrix.clear()

    # ===== Бегущая строка =====
    def generate_scrolling_text(self):
        if not self.session_active:
            return
        text = self.text_input.text()
        self.frames.clear()
        cols = build_text_columns(text)
        TOTAL = 32
        for shift in range(TOTAL, -len(cols)-1, -1):
            full = [[0]*TOTAL for _ in range(SIZE)]
            for i, col in enumerate(cols):
                x = shift + i
                if 0 <= x < TOTAL:
                    for y in range(7):
                        if col[y]:
                            full[y+4][x] = 1
            left, right = [], []
            for y in range(SIZE):
                left += full[y][:16]
                right += full[y][16:]
            self.frames.append({"left": left, "right": right})
        self.mark_modified()

    # ===== Кадры =====
    def add_frame(self):
        if not self.session_active:
            return
        self.frames.append({
            "left": self.left_matrix.get_frame(),
            "right": self.right_matrix.get_frame()
        })
        self.left_matrix.clear()
        self.right_matrix.clear()
        self.mark_modified()

    def save_frame_changes(self):
        if self.current_frame_index is None:
            return
        self.frames[self.current_frame_index] = {
            "left": self.left_matrix.get_frame(),
            "right": self.right_matrix.get_frame()
        }
        self.mark_modified()

    def load_frame_direct(self, index):
        self.current_frame_index = index
        frame = self.frames[index]
        self.left_matrix.load_frame(frame["left"])
        self.right_matrix.load_frame(frame["right"])

    # ===== JSON =====
    def save_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить JSON", "", "JSON (*.json)")
        if not path:
            return
        try:
            fps_val = int(self.fps_input.text() or 12)
        except ValueError:
            fps_val = 12
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"fps": fps_val, "loop": True, "frames": self.frames}, f, indent=2)
        self.session_file = path
        self.modified = False

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть JSON", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        frames = data.get("frames", [])
        fixed_frames = []
        for frame in frames:
            left = frame.get("left", [])
            right = frame.get("right", [])

            if left and isinstance(left[0], list):
                left = [bit for row in left for bit in row]
            if right and isinstance(right[0], list):
                right = [bit for row in right for bit in row]

            if len(left) != SIZE*SIZE:
                left = [0]*(SIZE*SIZE)
            if len(right) != SIZE*SIZE:
                right = [0]*(SIZE*SIZE)

            fixed_frames.append({"left": left, "right": right})

        self.frames = fixed_frames
        self.fps_input.setText(str(data.get("fps", 12)))
        if self.frames:
            self.load_frame_direct(0)
        self.session_active = True
        self.session_file = path
        self.modified = False

    def save_changes_to_file(self):
        if not self.session_file or not self.modified:
            print("Нет изменений для сохранения")
            return
        try:
            fps_val = int(self.fps_input.text() or 12)
        except ValueError:
            fps_val = 12
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump({"fps": fps_val, "loop": True, "frames": self.frames}, f, indent=2)
        self.modified = False
        print(f"Изменения сохранены в {self.session_file}")

    # ===== Анимация =====
    def start_animation(self):
        if not self.frames:
            return
        try:
            fps = int(self.fps_input.text())
            if fps <= 0:
                fps = 12
        except ValueError:
            fps = 12
        interval = int(1000 / fps)
        self.anim_index = 0
        self.anim_playing = True
        self.timer.start(interval)

    def stop_animation(self):
        self.anim_playing = False
        self.timer.stop()

    def play_step(self):
        if not self.anim_playing:
            return
        self.load_frame_direct(self.anim_index)
        self.anim_index = (self.anim_index + 1) % len(self.frames)

    # ===== Дополнительно =====
    def clear_all(self):
        self.left_matrix.clear()
        self.right_matrix.clear()
        self.mark_modified()

    def open_gallery(self):
        if not self.gallery:
            self.gallery = FramesGallery(self)
        self.gallery.refresh()
        self.gallery.show()

    def edit_frame(self):
        if not self.frames:
            return
        if not self.edit_gallery:
            self.edit_gallery = FrameEditGallery(self)
        self.edit_gallery.refresh()
        self.edit_gallery.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = EyesEditor()
    editor.show()
    sys.exit(app.exec())
