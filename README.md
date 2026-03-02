# RealLifeRL Setup Guide

## Prerequisites

- Python 3.10–3.13 → https://www.python.org/downloads/
- Git → https://git-scm.com/install/

## 1. Clone the Repository

```bash
git clone https://github.com/sycamore-lab-EPFL/RealLifeRL.git
cd RealLifeRL
```

## 2. Windows Setup

### 2.1 Install the Quanser SDK

The Quanser package is **not** on PyPI. We will install the SDK locally first.

Download and run the installer from:  
https://github.com/quanser/quanser_sdk_win64?tab=readme-ov-file

- Find the latest release of the SDK below the **About** section, on the right column of the page
- Download `install_quanser_sdk.exe` and run it
- Follow the installation steps

### 2.2 Set Up the Python Environment

Create and activate the virtual environment first, then install all packages inside it.

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install --upgrade --find-links "C:\Program Files\Quanser\Quanser SDK\python" "C:\Program Files\Quanser\Quanser SDK\python\quanser_api-2026.1.21-py2.py3-none-any.whl"
pip install numpy
```

**Note:** If installation fails, check that the wheel filename is correct at `C:\Program Files\Quanser\Quanser SDK\python\`

## 3. macOS Setup

### 3.1 Install the Quanser SDK

The Quanser package is **not** on PyPI. We will install the SDK locally first.

```bash
curl -L -o QLabs_mac.zip https://download.quanser.com/qlabs/latest/QLabs_Installer_mac64.zip
unzip QLabs_mac.zip -d QLabs_Installer_mac64
cd QLabs_Installer_mac64
chmod +x install_QLabs.sh
sudo ./install_QLabs.sh
cd .. && rm -rf QLabs_mac.zip QLabs_Installer_mac64
```

Allow Rosetta if prompted. The libraries are installed into `/opt/quanser/`.

### 3.2 Set Up the Python Environment

Create and activate the virtual environment first, then install all packages inside it.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install --upgrade --find-links /opt/quanser/python /opt/quanser/python/quanser_api-2025.10.20-py2.py3-none-any.whl
pip install numpy
```

**Note:** If installation fails, check that the wheel filename is correct with `ls /opt/quanser/python/`.

## Troubleshooting

- `ModuleNotFoundError: No module named '<module_name>'`  
  The venv is not activated:
  - Windows: `.venv\Scripts\activate`
  - macOS: `source .venv/bin/activate`

- `HIL Error`
  - The Qube-Servo has to be connected via USB
