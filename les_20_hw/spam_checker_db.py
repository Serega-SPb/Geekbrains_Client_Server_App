from datetime import datetime

from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableView, QGridLayout, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from test_ui import Ui_MainWindow as TestMainWindow


def transaction(func):
    def wrapper(*args, **kwargs):
        session = args[0].session
        try:
            res = func(*args, **kwargs)
        except Exception as ex:
            print(ex)
            session.rollback()
            return False
        else:
            session.commit()
            return res

    return wrapper


def add_row(model, row_ind, source, cols_field):
    col_ind = 0
    for f in cols_field:
        path = f.split('.')
        data = source
        for p in path:
            if p.startswith('['):
                data = data[int(p[1:-1])]
            else:
                data = getattr(data, p)

        item = QStandardItem(str(data))
        item.setEditable(False)
        model.setItem(row_ind, col_ind, item)
        col_ind += 1


def fill_table(table, data, headers, fields):
    model = QStandardItemModel(len(data), len(headers))
    model.setHorizontalHeaderLabels(headers)
    for i, d in enumerate(data):
        add_row(model, i, d, fields)
    table.setModel(model)


class TestDb:
    Base = declarative_base()

    class Data(Base):
        __tablename__ = 'data'

        id = Column(Integer, primary_key=True)
        text = Column(String)

        def __init__(self, text):
            self.text = text

        def __repr__(self):
            return f'Data({self.id}, {self.text})'

        def __str__(self):
            return self.text

    class History(Base):
        __tablename__ = 'history'

        id = Column(Integer, primary_key=True)
        search_text = Column(String)
        result_array = Column(String)
        time = Column(DateTime)

        def __init__(self, search, result):
            self.search_text = search
            self.result_array = result
            self.time = datetime.now()

    class Storage:
        DB = 'sqlite:///test.db'

        def __init__(self):
            self.database_engine = create_engine(self.DB, echo=False, pool_recycle=7200)
            TestDb.Base.metadata.create_all(self.database_engine)
            self.session_factory = sessionmaker(bind=self.database_engine)
            self.session = scoped_session(self.session_factory)()

        @transaction
        def add_data(self, text):
            data = TestDb.Data(text)
            self.session.add(data)

        @transaction
        def add_history(self, search, result):
            hist = TestDb.History(search, result)
            self.session.add(hist)

        def get_data(self):
            return self.session.query(TestDb.Data).all()

        def get_history(self):
            return self.session.query(TestDb.History).all()

        def get_data_like(self, search):
            return self.session.query(TestDb.Data).filter(TestDb.Data.text.like(search)).all()


class TestWindow(QMainWindow):

    TABS = {
        'Data': (['id', 'text'], ),
        'History': (['id', 'search', 'result', 'time'], ['id', 'search_text', 'result_array', 'time'])
    }

    def __init__(self):
        super().__init__()
        # loadUi('test.ui', self)
        self.ui = TestMainWindow()
        self.ui.setupUi(self)
        self.storage = TestDb.Storage()
        self.__init_ui()
        self.__init_tabs()
        self.load_tables()

    def __init_ui(self):
        self.ui.addBtn.clicked.connect(self.add_data)
        self.ui.searchBtn.clicked.connect(self.start_search)

        self.timer_refresh = QTimer()
        self.timer_refresh.setInterval(5000)
        self.timer_refresh.timeout.connect(self.load_tables)

    def __init_tabs(self):
        self.tables = {}
        self.ui.dbTabControl.clear()
        for t, c in self.TABS.items():
            grid = QGridLayout(self)
            table = QTableView(self)
            table.setObjectName(t.lower())
            grid.addWidget(table)
            self.tables[t] = table
            self.ui.dbTabControl.addTab(table, t)

    def load_tables(self):
        for table, wid in self.tables.items():
            func_name = f'get_{table.lower()}'
            data = getattr(self.storage, func_name)()
            headers, fields = self.TABS[table][0], self.TABS[table][-1]
            fill_table(wid, data, headers, fields)

    @property
    def data(self):
        return self.ui.inputTbx.text()

    def add_data(self):
        self.storage.add_data(self.data)
        self.ui.inputTbx.clear()
        self.load_tables()

    def start_search(self):

        result = self.storage.get_data_like(self.data)
        self.storage.add_history(self.data, ','.join([str(r) for r in result]))
        msbx = QMessageBox.information(self, 'Result', '\n'.join([str(r) for r in result]))
        self.ui.inputTbx.clear()
        self.load_tables()


def main():
    app = QApplication([])
    win = TestWindow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
