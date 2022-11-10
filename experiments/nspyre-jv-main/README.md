# nspyre-jv
Experiment control code based on nspyre: https://nspyre.readthedocs.io/en/latest/

## nspyre installation instructions
Please make sure that any changes to these packages, particularly nspyre, are done in a new environment! <br />
See instructions for creating a new environment here: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html. To create the environment, recommended to clone miniconda <br />

### recommended to run in a console emulator
cmder works well: https://github.com/cmderdev/cmder <br />
for installation, have to add correct folder to path <br />
following "another way of doing it in miniconda" instructions in this link: https://stackoverflow.com/questions/54959918/anaconda-python-cmder-integration-on-windows-10 <br />

### install git
https://github.com/git-guides/install-git <br />
each new nspyre user should make their own personal git account and be added to the lab git <br />
please make sure to work on your own personal branch, not "main", and then push/pull changes to/from main <br />
this is very important, so that personal bugs/changes are not reflected in everyone's code! <br />

### clone the repo
git clone https://github.com/nspyre-org/nspyre # only have to do this once <br />
cd nspyre <br />
git checkout newapi # make sure to use the "newapi" branch, jan 2022 version <br />

### make the conda env and install packages
conda create --name nsp python=3.9 <br />
conda activate nsp <br />
conda install rpyc pyqt=5.12.3 pyqtgraph=0.12.3 <br />
conda install lantz <br />
pip install wait_for2 <br />
pip install --no-deps -e . <br />
pip install grpcio # for connecting to pulse streamer <br />
pip install google # for connecting to pulse streamer <br />
pip install protobuf # for connecting to pulse streamer <br />
pip install cython # for connecting to spectrometer <br />
pip install andor # for connecting to spectrometer <br />
pip install pyqt5, pyqt6

### install packages for nspyre-jv
conda install tqdm # for instrument control <br />
pip install pylablib # for GUI <br />
pip install websocket # for GUI <br />

## startup instructions for a simple example spyrelet
start 3 new consoles in cmd console editor

### console 1, run the data server
conda activate nsp <br />
nspyre-dataserv <br />

### console 2, run the instrument server
conda activate nsp <br />
python C:\Users\Public\nspyre-jv\Instruments\Inserv\inserv_none.py <br />
python C:\Users\Public\nspyre-jv\Instruments\Inserv\inserv_all.py <br />

### console 3, run nspyre
conda activate nsp <br />
python C:\Users\Public\nspyre-jv\Spyrelets\Shared\counts_vs_time\counts_vs_time_app.py <br />
note that the above command is probably buggy as is, need to fix a good example spyrelet
