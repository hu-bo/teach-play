from setuptools import setup, find_packages

setup(
    name="teachplay-recorder-sdk",
    version="0.1.0",
    description="TeachPlay Recorder SDK - Screen capture and event recording",
    author="TeachPlay",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pynput>=1.7.6",
        "mss>=9.0.0",
        "pillow>=10.0.0",
        "pyobjc-framework-Quartz>=10.0;sys_platform=='darwin'",
        "pywin32>=306;sys_platform=='win32'",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
