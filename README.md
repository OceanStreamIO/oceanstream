# oceanstream

## How to install

### Prerequisites

- **Python 3.9**: Ensure you have Python 3.9 installed.

### Setup

If you wish to contribute or simply want to have a local copy of the code, you can clone the OceanStream repository. We recommend cloning from the dev branch as it contains the latest development changes:

    git clone -b dev https://github.com/OceanStreamIO/oceanstream.git

After cloning, navigate to the oceanstream directory:

    cd oceanstream
From here, you can install dependencies, run tests, or start development!
All pull requests should be directed to the dev branch.

### Using conda/mamba

    conda create -n oceanstream --yes python=3.9 --file requirements.txt --file requirements-dev.txt

### Using pip

1. Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
    This command creates a virtual environment in the `.venv` directory.
    The virtual environment should use Python 3.9.

- **Example using `pyenv`**:

    - If you're using `pyenv`, you can install Python 3.9 with:
    ```bash
    pyenv install 3.9
    ```

    - Navigate to Your Project Directory:
    ```bash
    cd /path/to/your/project_directory
    ```

    - Using the Python 3.9 executable managed by `pyenv`, create the virtual environment:
    ```bash
    ~/.pyenv/versions/3.9/bin/python -m venv .venv
    ```

2. Activate the virtual environment:
Note: In this context, `<venv_directory>` refers to `.venv`.
* On Linux and MacOS
    ```bash
    source <venv_directory>/bin/activate
    ```
* On Windows:
    ```bash
    # In cmd.exe
    <venv_directory>\Scripts\activate.bat
    # In PowerShell
    <venv_directory>\Scripts\Activate.ps1
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt # only for development needs
    ```

## Running pre-commit locally

### Installation:
First, you need to install the pre-commit tool. You can do this using pip:

    pip install pre-commit

### Installing the Git Hook Scripts:
Navigate to your repository where the .pre-commit-config.yaml file is located. Install the Git hook scripts with the following command:

    pre-commit install

This command installs the pre-commit script in your .git/hooks/ directory, allowing it to run automatically before each commit.

### Running pre-commit:
With everything set up, pre-commit will now run automatically every time you attempt to make a commit. If any of the hooks fail, the commit will be blocked, and you'll be prompted to fix the issues before committing again.

If you wish to manually run all hooks against all the files to see what might fail in advance, use:

    pre-commit run --all-files

### Updating Hooks:
As hooks receive updates or if the configuration in .pre-commit-config.yaml changes, you can update your hooks to the latest versions with:

     pre-commit autoupdate

### Skipping Hooks:
If, for some reason, you need to bypass the hooks for a particular commit, you can use the -n or --no-verify option:


    git commit -m "Your commit message" -n

### Uninstalling pre-commit:
If you decide to stop using pre-commit or need to reinstall it, you can uninstall the Git hook scripts with:


    pre-commit uninstall

With the configuration file already in the repository, setting up pre-commit is straightforward. It ensures that all contributors to the repo maintain a consistent code quality and adhere to the defined guidelines.

## Building documentation locally

### Prerequisites

Ensure you have Python and pip (Python package installer) installed on your system.

### Steps

1. Install Sphinx:

    Install Sphinx using pip. This is a one-time setup step.

        pip install sphinx

2. Navigate to Your Project's docs Directory:

    Open a terminal (or Command Prompt on Windows) and navigate to the docs directory of your project.

3. Build the Documentation:

    For Linux/Mac:

        make html

    For Windows:

        make.bat html

    This command will generate the HTML documentation in the build/html directory within your docs folder.
