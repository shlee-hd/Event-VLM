from setuptools import setup, find_packages

setup(
    name="event-vlm",
    version="0.1.0",
    description="Event-VLM: Scalable Vision-Language Models for Real-Time Industrial Surveillance",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/YOUR_USERNAME/event-vlm",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "transformers>=4.36.0",
        "ultralytics>=8.0.0",
        "hydra-core>=1.3.0",
        "optuna>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "isort>=5.12.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
