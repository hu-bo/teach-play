from setuptools import setup, find_packages

setup(
    name="teachplay-playback-sdk",
    version="0.1.0",
    description="TeachPlay Playback SDK - Step replay and event simulation",
    author="TeachPlay",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pynput>=1.7.6",
        "pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
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
