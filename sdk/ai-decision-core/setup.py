from setuptools import setup, find_packages

setup(
    name="teachplay-ai-decision-core",
    version="0.1.0",
    description="TeachPlay AI Decision Core - AI decision engine",
    author="TeachPlay",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pillow>=10.0.0",
    ],
    extras_require={
        "openai": [
            "openai>=1.0.0",
        ],
        "anthropic": [
            "anthropic>=0.18.0",
        ],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.18.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)
