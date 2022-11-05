# Simple ODMR
This code example runs a fake ODMR experiment. To run the experiment, first 
[install](https://nspyre.readthedocs.io/en/latest/install.html) nspyre.

Create an instrument server that hosts the fake instrument driver.
```bash
python3 inserv_odmr.py
```

Next, start the nspyre data server.
```bash
nspyre-dataserv
```
Finally, run the GUI application.
```bash
python3 app.py
```

You can also run the ODMR experiment from the command line.
```bash
python3 odmr.py
```
