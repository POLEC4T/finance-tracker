# Install dependencies
run the command below to install the dependencies
```bash
pip install -r requirements.txt
```

# How to use
First, you need to create a folder named "datas" and put the csv files of your operations in it (any name of file).

Then, run the command below to generate the outputs files for the graph.

```bash
python add_operations.py
```

Finally, run the command below to generate the graph.
```bash
python graph.py
```

# config file
You can change the config file to 
- change the output filenames
- change the csv delimiter
- change the csv folder
- set if you want to ask before writing operations with already existing libelle






