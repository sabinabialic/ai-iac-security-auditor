# Automated IaC Security Auditor

## The Problem
Manually reviewing IaC files for security misconfigurations is time-consuming and error-prone. It's easy to miss issues like publicly exposed S3 buckets, unrestricted security groups, or missing encryption.

## The Solution
Build an AI assistant that automatically scans Terraform code, identifies potential security vulnerabilities, explains the risk, and suggests the corrected code block. This leverages an LLM's ability to understand code and security best practices.

## Features
- **Code Scanning:** Ingests a Terraform file (.tf) or an entire directory.
- **Vulnerability Detection:** Uses an LLM with a specialized prompt to find common security issues (e.g., hardcoded secrets, overly permissive IAM roles).
- **Risk Explanation:** The LLM explains why the identified code is a security risk.
- **Automated Fixes:** The assistant provides a corrected, secure version of the code snippet.

## Technologies Used
- **Language:** Python
- **Core AI:** LangChain
- **LLM:** CodeLlama, available via Hugging Face.
- **Interface:** A CLI tool that can be integrated directly into a CI/CD pipeline.

## Who Benefits?
Developers get instant, actionable feedback on their Terraform code directly in their workflow, allowing them to learn and fix security issues on the spot without waiting for a manual review.

DevOps & Security teams can enforce security standards automatically across all projects, reducing the risk of human error and ensuring a consistent security baseline for all cloud infrastructure.

## How It's Used
### As a Local Developer Tool
A developer runs your CLI assistant on their machine against a .tf file. The tool immediately provides a report detailing any security issues, explaining the risks, and providing corrected code snippets.

### As an Automated CI/CD Guardrail
The tool is integrated into a CI/CD pipeline (e.g., as a GitHub Action). When a developer submits a pull request with Terraform changes, the action runs automatically. If vulnerabilities are found, it can fail the build or post a comment on the PR, preventing insecure code from being merged.

### Usage
To use this action in your workflow, you can reference it as follows:

```
- name: Run AI Security Auditor
  # Now references your public, versioned action
  uses: sabinabialic/ai-iac-security-auditor@v1
  with:
    filepath: ${{ github.event_name == 'workflow_dispatch' && github.event.inputs.filepath || 'test' }}
  env:
    HUGGING_FACE_HUB_TOKEN: ${{ secrets.HUGGING_FACE_HUB_TOKEN }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Development
1. Create and activate a virtual environment:
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

2. Install the necessary Python libraries:
  ```
  pip install -r requirements.txt
  ```
