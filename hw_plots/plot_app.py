from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

from main_ui import Ui_MainWindow
from db_analysis import DbAnalysis


class PlotMainWindow(QMainWindow):

    numpy_funcs = {k: v for k, v in np.__dict__.items() if hasattr(v, '__call__')}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.db_analysis = DbAnalysis('sqlite:///server_db.db')
        self.__init_ui()

    def __init_ui(self):
        [self.init_task(i) for i in range(1, 4)]
        self.__init_history_histogramm()
        self.__init_messages_histogramm()

    def get_min_x(self, task_num):
        return getattr(self.ui, f'task{task_num}MinRangeXDsb')

    def get_max_x(self, task_num):
        return getattr(self.ui, f'task{task_num}MaxRangeXDsb')

    def get_step(self, task_num):
        return getattr(self.ui, f'task{task_num}StepRangeXDsb')

    def get_plot(self, task_num):
        return getattr(self.ui, f'task{task_num}PlotLayout')

    def get_apply_btn(self, task_num):
        return getattr(self.ui, f'task{task_num}ApplyBtn')

    def init_task(self, num):
        figure = Figure()
        canvas = FigureCanvas(figure)
        setattr(self, f't{num}_canvas', canvas)
        self.get_plot(num).addWidget(canvas)
        self.get_step(num).setValue(1)
        calc_func = getattr(self, f'task{num}_calc')
        self.update_canvas(canvas, calc_func())
        self.get_apply_btn(num).clicked.connect(lambda: self.update_canvas(canvas, calc_func()))

    def task1_calc(self):
        x_start = self.get_min_x(1).value()
        x_end = self.get_max_x(1).value()
        step = self.get_step(1).value()
        x_values = np.arange(x_start, x_end, step)
        y_values = x_values * 2 - np.cos(x_values)
        return x_values, y_values

    def task2_calc(self):
        x_start = self.get_min_x(2).value()
        x_end = self.get_max_x(2).value()
        step = self.get_step(2).value()
        x_values = np.arange(x_start, x_end, step)
        y_values = x_values ** 3 - np.sqrt(x_values)
        return x_values, y_values

    def task3_calc(self):
        math_func_str = self.ui.task3MathFuncLne.text()
        if not math_func_str or not math_func_str.startswith('y='):
            return
        math_func_str = math_func_str[2:]
        math_func_str = math_func_str.replace('^', '**')
        x_start = self.get_min_x(3).value()
        x_end = self.get_max_x(3).value()
        step = self.get_step(3).value()
        x_values = np.arange(x_start, x_end, step)
        try:
            y_values = eval(math_func_str.replace('x', 'x_values'), self.numpy_funcs, locals())
        except Exception as e:
            print(e)
            return
        return x_values, y_values

    @staticmethod
    def update_canvas(canvas, data):
        if not data or len(data) != 2 or not data[0].any():
            return
        figure = canvas.figure
        figure.clear()
        axis = figure.add_subplot()
        axis.plot(*data, 'r.-')
        axis.set(xlabel='X', ylabel='Y')
        canvas.draw()

    def __init_history_histogramm(self):
        figure = Figure()
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)
        layout = self.get_plot(4)
        label = QLabel(self)
        label.setText('History histogramm')
        label.setAlignment(Qt.AlignHCenter)
        label.setMaximumHeight(35)
        layout.addWidget(label, 0, 0)
        layout.addWidget(canvas, 1, 0)
        layout.addWidget(toolbar, 2, 0)
        self.history_canvas = canvas
        data = self.db_analysis.get_history_hist_data()

        axis = figure.add_subplot()
        axis.hist(data, bins=len(data))
        canvas.draw()

    def __init_messages_histogramm(self):
        figure = Figure()
        canvas = FigureCanvas(figure)
        self.get_plot(5).addWidget(canvas)
        self.get_apply_btn(5).clicked.connect(lambda: self.update_chat_users_hist(canvas))

    def update_chat_users_hist(self, canvas):
        figure = canvas.figure
        figure.clear()
        username = self.ui.task5UsernameLne.text()
        if not username:
            return
        data = self.db_analysis.get_message_stats_by_name(username)
        if not data:
            return

        labels, values = data.keys(), data.values()
        axis = figure.add_subplot()
        axis.pie(values, labels=labels, autopct='%1.1f%%')
        axis.axis('equal')
        canvas.draw()


def main():
    app = QApplication([])
    win = PlotMainWindow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
