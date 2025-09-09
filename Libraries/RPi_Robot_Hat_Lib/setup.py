from setuptools import setup, find_packages

setup(
    name="RPi_Robot_Hat_Lib",
    version="1.2.2",
    description="Raspberry Pi Robot Hat Library with encoder support",
    py_modules=["RPi_Robot_Hat_Lib", "Encoder"],
    install_requires=[
        "smbus2",
        "rpi-lgpio",
    ],
    python_requires=">=3.7",
)
