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

## Building Documentation Locally

### Prerequisites

Ensure you have Python and pip (Python package installer) installed on your system.

### Steps

#### 1) Install Sphinx:

Install Sphinx using pip. This is a one-time setup step.

    pip install sphinx

#### 2) Navigate to Your Project's docs Directory:

Open a terminal (or Command Prompt on Windows) and navigate to the docs directory of your project.

#### 3) Build the Documentation:

For Linux/Mac:

    make html

For Windows:

    make.bat html

This command will generate the HTML documentation in the build/html directory within your docs folder.
