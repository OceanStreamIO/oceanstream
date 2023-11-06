# oceanstream

The test data should download with the repo.
1. Ensure Git LFS is Installed:

Before cloning, make sure Git LFS is installed on your machine. 
You can download and install it from the Git LFS website, 
or use a package manager if available on your system.

For example:

On macOS (using Homebrew):

    brew install git-lfs

On Ubuntu/Debian (using apt):

    sudo apt-get install git-lfs

After installation, run the following command to set up Git LFS:

    git lfs install

2. Clone the Repository:

Use the standard git clone command to clone the repository. 
Git LFS will automatically manage the LFS-tracked files during the clone operation.


    git clone <repository-url>

Replace <repository-url> with the URL of your Git repository.

3. Git LFS Fetches the Files:

During cloning, Git LFS will fetch the LFS objects and 
replace the pointer files in your working directory with the actual large files.

4. Verify the Files:

After cloning, you can verify that the LFS files have been properly 
downloaded by checking their size or opening them. 
The files should be the actual large files, not the text pointers.
In some cases, if you clone a repository and the LFS files are not downloaded 
(you only see the pointer files), you may need to run:

    git lfs pull

This command will download any missing LFS objects for the current branch.