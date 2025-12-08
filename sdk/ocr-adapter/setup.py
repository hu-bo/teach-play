from setuptools import setup, find_packages

setup(
    name="teachplay-ocr-adapter",
    version="0.1.0",
    description="TeachPlay OCR Adapter - Unified OCR interface",
    author="TeachPlay",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pillow>=10.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "paddle": [
            "paddleocr>=2.7.0",
            "paddlepaddle>=2.5.0",
        ],
        "openai": [
            "openai>=1.0.0",
        ],
        "anthropic": [
            "anthropic>=0.18.0",
        ],
        "all": [
            "paddleocr>=2.7.0",
            "paddlepaddle>=2.5.0",
            "openai>=1.0.0",
            "anthropic>=0.18.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)
