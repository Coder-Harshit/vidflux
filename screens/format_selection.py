from email.mime import audio
from PySide6 import QtWidgets
from pandas import DataFrame

class FormatSelector(QtWidgets.QDialog):
    def __init__(self, parent, formats: DataFrame):
        super().__init__()
        print(formats)
        self.setWindowTitle("Select Format")
        self.setGeometry(100, 100, 300, 200)
        self.formats: DataFrame = formats
        self.selected_fmt_id = {
            'audio': None,
            'video': None,
        }

        base_layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel("Select format:", self)
        base_layout.addWidget(self.label)

        ###########################################################################
        # AUDIO!!!

        audio_layout = QtWidgets.QVBoxLayout()
        audio_layout.setObjectName("audio_layout")
        self.audio_enabled: bool = QtWidgets.QCheckBox("Enable Audio", self)
        self.audio_enabled.setChecked(True)
        self.audio_enabled.stateChanged.connect(self.toggle_audio)

        audio_layout.addWidget(self.audio_enabled)

        audio_options_layout = QtWidgets.QGridLayout(self)
        audio_options_layout.setObjectName("audio_options_layout")

        self.audio_radio_buttons = []
        audio_formats = self.formats[self.formats['vcodec'] == 'none']
        audio_formats = audio_formats[::-1]
        audio_group_btns = QtWidgets.QButtonGroup(self)

        col_count = 3
        for indx, (id, row) in enumerate(audio_formats.iterrows()):
            if row['language'] is None:
                text_str = f"{row['ext']}"
            else:
                text_str = f"{row['ext']}\t[{row['language']}]"
            radio_btn = QtWidgets.QRadioButton(
                # audio_options_layout,
                text_str,
            )

            radio_btn.setToolTip(
                f"""Id: {id}\nAudio codec: {row['acodec']}\nBitrate: {row['bitrate']}"""
            )
            radio_btn.format_id = id
            row_pos = indx // col_count
            col_pos = indx % col_count
            audio_options_layout.addWidget(radio_btn, row_pos, col_pos)
            self.audio_radio_buttons.append(radio_btn)
            # Use a unique integer ID for button group, but keep original format ID in the button
            # Extract numeric part for button ID, handling cases like "140" and "140-drc"
            try:
                parts = str(id).split('-')
                button_id = int(parts[0])
            except (ValueError, AttributeError):
                button_id = 10000 + id  # Use large offset to avoid conflicts
                
            audio_group_btns.addButton(radio_btn, button_id)
            # radio_btn.toggled.connect(self.update_selected_format)

        base_layout.addLayout(audio_layout)
        base_layout.addLayout(audio_options_layout)
        ###########################################################################

        ###########################################################################
        # VIDEO!!!
        video_layout = QtWidgets.QVBoxLayout()
        video_layout.setObjectName("video_layout")
        self.video_enabled: bool = QtWidgets.QCheckBox("Enable Video", self)
        self.video_enabled.setChecked(True)
        
        self.video_enabled.stateChanged.connect(self.toggle_video)

        video_layout.addWidget(self.video_enabled)

        video_options_layout = QtWidgets.QGridLayout(self)
        video_options_layout.setObjectName("video_options_layout")

        self.video_radio_buttons = []
        video_formats = self.formats[self.formats['acodec'] == 'none']
        video_formats = video_formats[::-1]
        video_group_btns = QtWidgets.QButtonGroup(self)

        col_count = 3
        for indx, (id, row) in enumerate(video_formats.iterrows()):
            radio_btn = QtWidgets.QRadioButton(
                f"{row['resolution'].split("x")[-1]}p\t\t[{row['ext']}]",
                # parent=video_options_layout,
                )
            radio_btn.setToolTip(f"Video codec: {row['vcodec']}\nBitrate: {row['bitrate']}")
            radio_btn.format_id = id
            row_pos = indx // col_count
            col_pos = indx % col_count
            video_options_layout.addWidget(radio_btn, row_pos, col_pos)
            self.video_radio_buttons.append(radio_btn)
            video_group_btns.addButton(radio_btn, int(id))
            # radio_btn.toggled.connect(self.update_selected_format)

        base_layout.addLayout(video_layout)
        base_layout.addLayout(video_options_layout)
        ###########################################################################
        # Buttons
        self.ok_btn = QtWidgets.QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.confirm_selection)
        base_layout.addWidget(self.ok_btn)


    def confirm_selection(self):
        audio_selected = False
        video_selected = False

        if not self.audio_enabled.isChecked() and not self.video_enabled.isChecked():
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select at least one format.")
            return

        for radio_btn in self.audio_radio_buttons:
            if radio_btn.isChecked():
                self.selected_fmt_id['audio'] = radio_btn.format_id
                audio_selected = True
                break

        for radio_btn in self.video_radio_buttons:
            if radio_btn.isChecked():
                self.selected_fmt_id['video'] = radio_btn.format_id
                video_selected = True
                break

        if not audio_selected and not video_selected:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select at least one format.")
            return

        self.accept()

    def get_selected_formats(self):
        return self.selected_fmt_id
    
    def toggle_audio(self, state):
        if state:
            for radio_btn in self.audio_radio_buttons:
                radio_btn.show()
        else:
            for radio_btn in self.audio_radio_buttons:
                radio_btn.hide()

    def toggle_video(self, state):
        if state:
            for radio_btn in self.video_radio_buttons:
                radio_btn.show()
        else:
            for radio_btn in self.video_radio_buttons:
                radio_btn.hide()