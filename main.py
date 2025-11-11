import sys, os, ctypes
from PyQt5 import QtCore, QtGui, QtWidgets


class DesktopPet(QtWidgets.QLabel):
    def __init__(self, image_path):
        super().__init__()

        # Load transparent PNG
        self.original_pixmap = QtGui.QPixmap(image_path)
        self.flipped = self.original_pixmap.transformed(QtGui.QTransform().scale(-1, 1))

        # Set image
        self.setPixmap(self.original_pixmap)
        self.resize(self.original_pixmap.size())

        # Remove window frame, make always on top and transparent
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.update_screen_rect()

        self.screen_rect = QtWidgets.QApplication.primaryScreen().geometry()

        self.speed = 1
        self.direction = 1
        self.moving = True

        start_x = self.screen_rect.x() + self.screen_rect.width() // 2 - self.width() // 2
        start_y = self.screen_rect.y() + self.screen_rect.height() - self.height() - 46
        self.move(start_x, start_y)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(16)

        # Track dragging
        self.drag_position = None

        # Create context menu
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction("Say Hello", self.say_hello)
        self.menu.addSeparator()
        self.menu.addAction("Exit", QtWidgets.qApp.quit)

        # Show the pet
        self.show()

        

    def update_screen_rect(self):
        screen = QtWidgets.QApplication.screenAt(self.pos())
        if screen is None:
            screen = QtWidgets.QApplication.primaryScreen()
        self.screen_rect = screen.availableGeometry()

    def loop(self):
        self.update_screen_rect()

        if self.moving:

            x = self.x() + (self.speed * self.direction)
            y = self.y()

            if x < self.screen_rect.x() or x + self.width() > self.screen_rect.x() + self.screen_rect.width():
                self.direction *= -1
                self.setPixmap(self.flipped if self.direction == -1 else self.original_pixmap)
                x = max(self.screen_rect.x(), min(x, self.screen_rect.x() + self.screen_rect.width() - self.width()))

            self.move(x,y)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.moving = False
        elif event.button() == QtCore.Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.moving = True

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


    def show_context_menu(self, pos):
        self.menu.exec_(pos)

    def say_hello(self):
        QtWidgets.QMessageBox.information(self, " ", "Meow!")

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pet = DesktopPet(resource_path("idle.png"))
    sys.exit(app.exec_())
