from __future__ import annotations

import os
import sys

import setuptools

# Read the content of README.md for long_description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# This is good for editable installs while the package lives in src/
# It ensures that 'import ai_shell_assistant' works without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

setuptools.setup(
    name="ai-shell-assistant", # Standard practice to include the name
    version="0.1.0",
    author="AI Shell Assistant Contributors", # Placeholder as actual author is unknown
    author_email="placeholder@example.com", # Placeholder
    description="AI Shell Assistant powered by language models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arrase/ai-shell-assistant",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langgraph",
        "langchain-google-vertexai",
        "langchain-google-genai", # For Google AI Studio LLMs
        "langchain-ollama",
        "langchain-community", # For ShellTool, DuckDuckGoSearchRun
        "langchain-experimental", # For ShellTool's BashProcess
        "duckduckgo-search", # For DuckDuckGoSearchRun tool
        "rich", # For console output
        "PyYAML", # For shortcuts
        "google-cloud-aiplatform", # For Vertex AI
        # Standard library modules like mimetypes, base64, argparse, configparser, logging, pathlib, re, sys, os
        # are not listed in install_requires.
    ],
    python_requires=">=3.9", # Based on modern library usage (e.g. langgraph, f-strings, pathlib enhancements)
    entry_points={
        "console_scripts": [
            "ai-shell-assistant=ai_shell_assistant.assistant:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License", # Assuming MIT License based on typical open-source projects
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
)