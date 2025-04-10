# Environment Setup Instructions

## 1. Setup Docker

### a. Docker Installation
Install Docker on your machine by following the instructions provided in the [official Docker installation guide](https://docs.docker.com/get-docker/).

### b. Test Docker Installation
1. Open your command line and run the following command:
   ```
   docker run hello-world
   ```
2. You should see output indicating that Docker is installed correctly.

### c. Troubleshooting
#### a. Windows
1. **Docker is hanging on start up**
   1. Solution:
      1. Uninstall Docker
      2. Reboot your computer
      3. Install a Linux WLS if you don't have one
      4. Reinstall Docker
2. **No hypervisor is present in the system**
   1. Run:
   ```
   bcdedit /set hypervisorlaunchtype auto
   ```
   2. Reboot your computer
#### b. Mac Intel
#### c. Mac M1/M2
#### d. Linux
## 2. Setup Visual Studio Code

### a. Install VS Code
Download and install [Visual Studio Code (VS Code)](https://code.visualstudio.com/) on your machine.

### b. Install Extensions
1. Install the Remote-SSH extension:
   - Click the Extensions button in VS Code.
   - Search for "Remote-SSH" and click Install.
   
2. Install the Remote-Explorer extension:
   - Search for "Remote-Explorer" in the Extensions marketplace and install it.

### c. Docker Extensions
Install the following Docker extensions:
- Docker
- Remote - Containers

### d. Optional Extensions
Optionally, you can install other useful extensions such as:
- Go

## 3. Setup the Container Environment

### a. Open the Project
Open your project directory with Visual Studio Code, making sure that the Dockerfile is located in the root of the directory you've opened in VS Code.

### b. Remote Development
Open the Remote Window by clicking the icon on the bottom left of the VS Code window.

### c. Reopen in Container
Choose "Reopen in Container" from the command palette.

### d. Dockerfile Configuration
Select "From 'Dockerfile'" when prompted to refer to the existing Dockerfile in the container configuration.

### e. Environment Ready
After selecting the features(no additional features are needed to complete the projects) and waiting for a few minutes, your environment will be ready. Subsequent openings of this folder will be instantaneous. 