from setuptools import setup, find_packages

setup(
    name="minecraft-server-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "discord.py",
        "python-dotenv",
        "plyer",
        "psutil"
    ],
) 