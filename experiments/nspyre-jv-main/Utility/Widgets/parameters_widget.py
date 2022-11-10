# @Author: Eric Rosenthal
# @Date:   2022-03-24T09:27:02-07:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T15:39:57-07:00



from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QLabel, QVBoxLayout, QWidget, QComboBox, QLineEdit
from pyqtgraph import SpinBox

class ParamsWidget(QWidget):
    """Create a simple GUI widget containing a list of parameters.

    Typical usage example:

    .. code-block:: python

        self.params_widget = ParamsWidget({
                            'pulse_power': {'suffix': 'V', 'siPrefix': True},
                            'pulse_length': {'suffix': 's', 'siPrefix': True},
                            })

        def doSomething(self):
            print(f'Making a pulse with power = {self.params_widget.pulse_power} V, length = {self.params_widget.pulse_length} V'

    """

    def __init__(self, params: dict, experiment_name='unnamed experiment', *args, **kwargs):
        """Initialize params widget.

        Args:
            params: dictionary mapping parameter names to options, which are passed as arguments to their corresponding pyqtgraph spinbox. The options are documented at https://pyqtgraph.readthedocs.io/en/latest/widgets/spinbox.html.
        """

        super().__init__(*args, **kwargs)

        self.params = params

        if 'autosave_onoff' not in self.params:
            self.params['autosave_onoff'] = {'style':'checkbox', 'info':{'value':1, 'bounds':(0, 1), 'int':True}}

        self.spinboxes = {}
        self.checkboxes = {}

        # vertical layout
        total_layout = QVBoxLayout()

        # add parameter spinbox widgets to the layout
        for p in self.params:

            if self.params[p]['style'] == 'spinbox':
                # small layout containing a label and spinbox
                label_spinbox_layout = QHBoxLayout()
                # create parameter label
                label = QLabel()
                label.setText(p)
                label_spinbox_layout.addWidget(label)
                # create spinbox
                spinbox = SpinBox(**self.params[p]['info'])
                # store the spinboxes
                self.spinboxes[p] = spinbox
                label_spinbox_layout.addWidget(spinbox)

                total_layout.addLayout(label_spinbox_layout)
            elif self.params[p]['style'] == 'checkbox':

                if (p != 'autosave_onoff'):
                    # create checkbox
                    checkbox_name = p
                    checkbox = QCheckBox(checkbox_name)
                    checkbox.setChecked(self.params[checkbox_name]['info']['value'])
                    checkbox.stateChanged.connect(self.btnstate)

                    # store the checkbox
                    self.checkboxes[checkbox_name] = checkbox
                    total_layout.addWidget(checkbox)

            else:
                print('error: GUI_PARAMS must have specified style spinbox or checkbox')

        # add stretch element to take up any extra space below the spinboxes
        total_layout.addStretch()

        # add autosave button
        self.autosave_button = QCheckBox("Autosave")
        self.autosave_button.setChecked(self.params['autosave_onoff']['info']['value'])
        self.autosave_button.stateChanged.connect(lambda:self.autosave_btnstate(self.autosave_button))
        total_layout.addWidget(self.autosave_button)

        # text box for the user to enter the name of the desired data set in the dataserver
        try:
            self.dataset_lineedit = QLineEdit(experiment_name)
            self.dataset_lineedit.setReadOnly(True)
            dataset_layout = QHBoxLayout()
            dataset_layout.addWidget(QLabel('Experiment name:'))
            dataset_layout.addWidget(self.dataset_lineedit)
            # dummy widget containing the data set lineedit and label
            dataset_container = QWidget()
            dataset_container.setLayout(dataset_layout)
            total_layout.addWidget(dataset_container)
        except:
            print('Warning: no experiment name given.')
            pass

        # # box to choose different options
        # file type options for saving data
        # self.filetypes = {
        #     'name1': 'experiment_A',
        #     'name2': 'experiment_B',
        # }
        # # dropdown menu for selecting the desired filetype
        # self.filetype_combobox = QComboBox()
        # self.filetype_combobox.addItems(list(self.filetypes))
        # total_layout.addWidget(self.filetype_combobox)

        self.setLayout(total_layout)

    def all_params(self):
        """Return the current value of all user parameters as a dictionary."""
        all_params = {}

        # spinbox parameters
        try:
            for p in self.params:
                all_params[p] = self.spinboxes[p].value()
        except:
            pass

        # saving parameters
        all_params['autosave_onoff'] = self.params['autosave_onoff']['info']['value']

        return all_params

    def __getattr__(self, attr: str):
        """Allow easy access to the parameter values."""
        if attr in self.params:
            return self.spinboxes[attr].value()
        else:
            # raise the default python error when an attribute isn't found
            return self.__getattribute__(attr)

    def btnstate(self, state):
        button = self.sender()
        checkbox_name = button.text()
        if state:
            self.params[checkbox_name]['info']['value'] = 1
            print(checkbox_name + ' = True')
        else:
            self.params[checkbox_name]['info']['value'] = 0
            print(checkbox_name + ' = False')

    def autosave_btnstate(self,b):
        if b.isChecked():
            self.params['autosave_onoff']['info']['value'] = 1
            print("autosave on")
        else:
            self.params['autosave_onoff']['info']['value'] = 0
            print("autosave off")
