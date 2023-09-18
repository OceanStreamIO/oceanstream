# oceanstream

## How to install

### With conda/mamba

    conda create -n oceanstream --yes python=3.9 --file requirements.txt --file requirements-dev.txt


### With pip

    virtualenv oceanstream -p python3.9

This creates a new virtual environment named oceanstream using Python 3.9.

#### Activate the virtual environment:

On macOS and Linux:

    source oceanstream/bin/activate

On Windows:

    oceanstream\Scripts\activate

#### Install packages using pip:

    pip install -r requirements.txt
    pip install -r requirements-dev.txt

Now, you have a virtual environment named oceanstream with the packages specified in both requirements.txt and requirements-dev.txt installed.
