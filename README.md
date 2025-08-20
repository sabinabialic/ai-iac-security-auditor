# ai-iac-security-auditor

## Automated IaC Security Auditor

### The Problem
Manually reviewing IaC files for security misconfigurations is time-consuming and error-prone. It's easy to miss issues like publicly exposed S3 buckets, unrestricted security groups, or missing encryption.

### The Solution
Build an AI assistant that automatically scans Terraform code, identifies potential security vulnerabilities, explains the risk, and suggests the corrected code block. This leverages an LLM's ability to understand code and security best practices.

### Features
- **Code Scanning:** Ingests a Terraform file (.tf) or an entire directory.
- **Vulnerability Detection:** Uses an LLM with a specialized prompt to find common security issues (e.g., hardcoded secrets, overly permissive IAM roles).
- **Risk Explanation:** The LLM explains why the identified code is a security risk.
- **Automated Fixes:** The assistant provides a corrected, secure version of the code snippet.

### Technologies Used
- **Language:** Python
- **Core AI:** LangChain
- **LLM:** CodeLlama, available via Hugging Face.
- **Interface:** A CLI tool that can be integrated directly into a CI/CD pipeline.

## Development
1. Create and activate a virtual environment:
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

2. Install the necessary Python libraries:
  ```
  pip install langchain langchain-huggingface huggingface-hub python-hcl2
  ```
