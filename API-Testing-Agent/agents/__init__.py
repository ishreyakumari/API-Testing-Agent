"""
Simple Multi-Agent System

Two agents that work together:
1. DocumentClassifierAgent - Looks at documents and figures out what type they are
2. APITestingAgent - Tests APIs with those documents

Usage:
    from agents import DocumentClassifierAgent, APITestingAgent
"""

from .document_classifier_agent import DocumentClassifierAgent
from .api_testing_agent import APITestingAgent
from .workflow import run_workflow

__all__ = ["DocumentClassifierAgent", "APITestingAgent", "run_workflow"]
