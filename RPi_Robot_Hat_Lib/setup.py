from setuptools import setup, find_packages

setup(
    name='RPi_Robot_Hat_Lib',
    version='2.0.0',
    description='Raspberry Pi Robot Hat Library for MobileRobot Project',
    author='JiaLeChye',
    py_modules=['RPi_Robot_Hat_Lib'],
    install_requires=[
        'rpi-lgpio>=0.6',
        'adafruit-circuitpython-ssd1306',
        'adafruit-circuitpython-pca9685',
        'smbus2',
        'pillow',
        'numpy',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Hardware',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
