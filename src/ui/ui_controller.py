import os
import logging
from PySide6.QtCore import Qt, QRunnable, Slot, QThreadPool
from PySide6.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout, QPushButton, QHeaderView, QCheckBox, QLabel, \
    QLineEdit, QComboBox, QFormLayout

from src.core.task_project_manager import TaskProjectManager
from src.utils.config_programs import *
from src.utils.config_projects import *


class TaskWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(TaskWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        self.fn(*self.args, **self.kwargs)


class UIController:
    def __init__(self):
        self.thread_pool = QThreadPool()
        current_dir = os.getcwd()

        # 配置文件路径
        self.projects_json_path = os.path.join(current_dir, "assets", "config", "projects.json")
        self.programs_json_path = os.path.join(current_dir, "assets", "config", "programs.json")
        self.styles_json_path = os.path.join(current_dir, "assets", "config", "style.qss")

        # 加载配置
        self.projects = ProjectsJson.load_from_file(self.projects_json_path)
        self.programs = ProgramsJson.load_from_file(self.programs_json_path)

    def load_styles(self, widget):
        """加载样式文件"""
        with open(self.styles_json_path, 'r', encoding='utf-8') as f:
            widget.setStyleSheet(f.read())

    def refresh_resources(self):
        """刷新资源"""
        project = self.projects.projects[0]
        try:
            task_manager = TaskProjectManager()
            task_manager.create_tasker_process(project)
            task_manager.send_task(project, "RELOAD_RESOURCES")
            logging.info("任务 RELOAD_RESOURCES 已成功发送")
        except Exception as e:
            logging.error(f"发送任务 RELOAD_RESOURCES 失败: {e}")

    def on_table_item_changed(self, item):
        """处理表格内容变化"""
        data = item.data(Qt.UserRole)
        if data is None:
            return

        if isinstance(data, tuple):
            field, project = data
        else:
            project = data

        if item.column() == 2:
            project.adb_config.adb_path = item.text()
        elif item.column() == 3:
            project.adb_config.adb_address = item.text()

        self.projects.save_to_file(self.projects_json_path)

    def load_device_table(self, table,splitter,info_title):
        """加载设备表格数据"""
        for project in self.projects.projects:
            row = table.rowCount()
            table.insertRow(row)

            # 添加任务名称
            task_name_item = QTableWidgetItem(project.project_name)
            task_name_item.setData(Qt.UserRole, project)
            table.setItem(row, 0, task_name_item)

            # 添加游戏名称
            program_name_item = QTableWidgetItem(project.program_name)
            table.setItem(row, 1, program_name_item)

            # 添加ADB地址
            adb_address_item = QTableWidgetItem(project.adb_config.adb_path)
            adb_address_item.setData(Qt.UserRole, ('adb_path', project))
            table.setItem(row, 2, adb_address_item)

            # 添加ADB端口
            adb_port_item = QTableWidgetItem(project.adb_config.adb_address)
            adb_port_item.setData(Qt.UserRole, ('adb_address', project))
            table.setItem(row, 3, adb_port_item)

            # 添加运行状态
            status_item = QTableWidgetItem('正在执行')
            table.setItem(row, 4, status_item)

            # 添加操作按钮
            container_widget = self._create_operation_buttons(project,splitter,info_title)
            table.setCellWidget(row, 5, container_widget)

            table.setRowHeight(row, 50)

        self._setup_table_columns(table)

    def _create_operation_buttons(self, project,splitter,info_title):
        """创建操作按钮"""
        container_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 添加一键启动按钮
        button_task_connect = QPushButton('一键启动')
        button_task_connect.setObjectName('runButton')
        button_task_connect.clicked.connect(
            lambda _, p=project, b=button_task_connect: self.sent_task(p, b))
        layout.addWidget(button_task_connect)

        # 添加查看详情按钮
        button_info = QPushButton('查看详情')
        button_info.setObjectName('infoButton')
        button_info.clicked.connect(lambda _, p=project: self.show_device_details( p,splitter, info_title))
        layout.addWidget(button_info)

        container_widget.setLayout(layout)
        return container_widget

    def _setup_table_columns(self, table):
        """设置表格列宽"""
        table.resizeColumnsToContents()
        column_widths = [80, 80, 280, 130, 100]
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)

    def sent_task(self, project, button):
        """运行任务"""
        button.setText("正在连接")
        button.setEnabled(False)

        task_manager = TaskProjectManager()

        def execute_task():
            try:
                task_manager.create_tasker_process(project)
                project_run_data = project.get_project_run_data(self.programs)
                task_manager.send_task(project, project_run_data)
                button.setText("已连接")
                button.setEnabled(True)
            except Exception as e:
                logging.error(f"任务启动失败: {e}")
                button.setText("连接失败")
                button.setEnabled(True)

        task = TaskWorker(execute_task)
        self.thread_pool.start(task)

    def send_single_task(self, selected_task, project):
        """发送单个任务"""

        def execute_task():
            try:
                task_manager = TaskProjectManager()
                task_manager.create_tasker_process(project)

                project_run_data = project.get_project_all_run_data(self.programs)
                filtered_tasks = [task for task in project_run_data.project_run_tasks
                                  if task.task_name == selected_task.task_name]

                if not filtered_tasks:
                    logging.error(f"任务 {selected_task.task_name} 不在选中任务中")
                    return

                single_task_run_data = ProjectRunData(project_run_tasks=filtered_tasks)
                task_manager.send_task(project, single_task_run_data)
                logging.info(f"任务 {selected_task.task_name} 已成功发送")

            except Exception as e:
                logging.error(f"任务 {selected_task.task_name} 发送失败: {e}")

        task = TaskWorker(execute_task)
        self.thread_pool.start(task)

    def show_device_details(self,  project,splitter, info_title):
        # 更新详细信息标题
        info_title.setText(f"详细信息: {project.project_name}")

        # 清空之前的布局
        task_selection_group = splitter.widget(0)
        task_selection_layout = task_selection_group.layout()
        self.clear_layout(task_selection_layout)

        task_selection_group_1 = splitter.widget(1)
        task_selection_layout_1 = task_selection_group_1.layout()
        self.clear_layout(task_selection_layout_1)
        # 获取对应的 program
        program = self.programs.get_program_by_name(project.program_name)
        if not program:
            return

        # 记录所有复选框
        self.checkboxes = []

        # 动态添加任务复选框和设置按钮
        for task in program.program_tasks:
            task_row = QHBoxLayout()

            # 添加任务复选框
            checkbox = QCheckBox(task.task_name)
            checkbox.setChecked(task.task_name in project.selected_tasks)
            self.checkboxes.append(checkbox)

            # 定义复选框状态变化的处理函数
            def on_checkbox_state_changed(state, task_name=task.task_name):
                if state == Qt.CheckState.Checked.value:  # 勾选状态
                    if task_name not in project.selected_tasks:
                        project.selected_tasks.append(task_name)
                else:  # 未勾选状态
                    if task_name in project.selected_tasks:
                        project.selected_tasks.remove(task_name)

                # 保存到文件
                self.projects.save_to_file(self.projects_json_path)

            checkbox.stateChanged.connect(on_checkbox_state_changed)
            task_row.addWidget(checkbox)

            # 添加设置按钮
            set_button = QPushButton('设置')
            set_button.clicked.connect(
                lambda _, selected_task=task: self.set_task_parameters(selected_task, program, project,splitter))
            task_row.addWidget(set_button)

            # 添加发送任务按钮
            execute_button = QPushButton('执行')
            execute_button.clicked.connect(
                lambda _, selected_task=task: self.send_single_task(selected_task, project))
            task_row.addWidget(execute_button)

            task_selection_layout.addLayout(task_row)
        self.select_all_state = False
        # 添加“全选”和“开始”按钮
        button_container = QHBoxLayout()
        select_all_button = QPushButton("全选")
        start_button = QPushButton("开始")
        button_container.addWidget(select_all_button)
        button_container.addWidget(start_button)
        def toggle_select_all():
            if not self.select_all_state:
                # 全选所有任务
                for checkbox in self.checkboxes:
                    checkbox.setChecked(True)
                select_all_button.setText("清空")
                self.select_all_state = True
            else:
                # 清空所有任务的选择
                for checkbox in self.checkboxes:
                    checkbox.setChecked(False)
                select_all_button.setText("全选")
                self.select_all_state = False

        select_all_button.clicked.connect(toggle_select_all)
        start_button.clicked.connect(lambda _, p=project: self.sent_task(p, start_button))
        task_selection_layout.addLayout(button_container)

    def set_task_parameters(self, selected_task, program, project,splitter):
        """动态生成任务的参数设置界面"""
        task_settings_group = splitter.widget(1)
        task_settings_layout = task_settings_group.layout()
        self.clear_layout(task_settings_layout)

        # 获取对应任务的 option
        options = program.get_task_by_name(selected_task.task_name).option
        setting = program.option.options

        # 使用 QFormLayout 来对齐标签和输入框，使得布局更加整齐
        form_layout = QFormLayout()
        if not options:
            label = QLabel("该任务无参数设置项")
            form_layout.addRow(label)
            task_settings_layout.addLayout(form_layout)
            return

        for option in options:
            sett = setting.get(option)
            print(option)
            # 优先从 project.option 获取参数，如果不存在则使用 sett 的值
            project_option = next((opt for opt in project.option.options if opt.option_name == option), None)

            # 动态生成 QLineEdit、QComboBox 或 QCheckBox，并绑定其值到 project.option
            if sett.type == 'input' and sett.input:
                self.create_input_option(form_layout, project, project_option, sett, option)

            elif sett.type == 'select' and sett.select:
                self.create_select_option(form_layout, project, project_option, sett, option)

            elif sett.type == 'boole':
                self.create_boole_option(form_layout, project, project_option, sett, option)

            else:
                print(f"Unknown or missing attributes for option: {option}")        # 将生成的表单布局添加到主布局中
        task_settings_layout.addLayout(form_layout)

    def create_input_option(self, layout, project, project_option, sett, option_name):
        """创建 input 类型的参数设置控件"""
        label = QLabel(sett.input.name)

        # 获取默认值，优先从 project.option 获取
        default_value = project_option.option_value if project_option and project_option.option_type == 'input' else sett.input.default
        line_edit = QLineEdit(str(default_value))

        # 将输入框的内容变化绑定到 project.option
        line_edit.textChanged.connect(
            lambda text, name=option_name: self.update_project_option(project, name, 'input', text)
        )

        layout.addRow(label, line_edit)
        print(f"Input Option: name={sett.input.name}, default={default_value}")

    def create_select_option(self, layout, project, project_option, sett, option_name):
        """创建 select 类型的参数设置控件"""
        label = QLabel(option_name)
        combo_box = QComboBox()

        # 获取默认选中值，优先从 project.option 获取
        selected_value = project_option.option_value if project_option and project_option.option_type == 'select' else \
            sett.select[0].name

        # 添加下拉选项并设置默认选中项
        for select_option in sett.select:
            combo_box.addItem(select_option.name)
            if select_option.name == selected_value:
                combo_box.setCurrentText(select_option.name)

        # 处理下拉框选择事件
        combo_box.currentTextChanged.connect(
            lambda text, name=option_name: self.update_project_option(project, name, 'select', text)
        )

        layout.addRow(label, combo_box)

    def create_boole_option(self, layout, project, project_option, sett, option_name):
        """创建 boole 类型的参数设置控件"""
        label = QLabel(option_name)
        check_box = QCheckBox()

        # 获取 BooleOption 对象，优先从 project_option 获取
        if project_option and project_option.option_type == 'boole':
            boole_option = project_option.option_value
        else:
            boole_option = sett.boole

        # 如果 boole_option 是 BooleOption 类型，则取其 default 属性
        boole_value = boole_option.default if isinstance(boole_option, BooleOption) else boole_option
        check_box.setChecked(boole_value)

        # 处理复选框状态改变事件，更新 BooleOption 中的 default 属性
        check_box.stateChanged.connect(
            lambda state, name=option_name: self.update_project_option(project, name, 'boole', bool(state))
        )

        layout.addRow(label, check_box)

    def update_project_option(self, project, option_name, option_type, option_value):
        # 查找或创建 project.option 中的相应选项
        project_option = next((opt for opt in project.option.options if opt.option_name == option_name), None)

        if project_option:
            # 更新现有选项
            project_option.option_value = option_value
        else:
            # 如果选项不存在，创建新选项并添加到 project.option 中
            new_option = Option(option_name=option_name, option_type=option_type, option_value=option_value)
            project.option.options.append(new_option)

        self.projects.save_to_file(self.projects_json_path)

    def clear_layout(self, layout):
        """清空布局中的所有小部件"""
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    # 如果是布局项，递归清空其子布局
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clear_layout(sub_layout)  # 递归调用
        layout.update()  # 更新布局
