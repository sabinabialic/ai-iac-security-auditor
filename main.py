import argparse
import os
from github import Github
import hcl2
import json
import sys
from huggingface_hub import InferenceClient

# Environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
EVENT_PATH = os.getenv("GITHUB_EVENT_PATH")
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

SYSTEM_PROMPT = """You are a highly specialized and strict security auditor for Terraform code. Your ONLY task is to identify high-impact security vulnerabilities in the provided code block.

---
**CRITICAL INSTRUCTION: Your performance is judged on accuracy. You will be penalized for incorrectly identifying vulnerabilities in secure code. If you do not find a clear, high-impact vulnerability, you MUST follow the "no vulnerabilities" rule. Do NOT invent potential issues or suggest best-practice improvements if the code is already secure.**
---

**Definition of a Vulnerability:**
A vulnerability is a configuration that directly exposes a system to immediate and significant risk, such as public access (`0.0.0.0/0`), missing encryption, or `AdministratorAccess` IAM roles. Standard practices like hardcoding resource names are NOT vulnerabilities.

**Analysis Rules:**
1.  Analyze ONLY the provided Terraform code. Do not assume any context outside this code.
2.  If you find one or more clear vulnerabilities, your response MUST follow this exact format:
    - **Vulnerability:** [A one-sentence summary and its severity].
    - **Risk:** [A brief explanation of the risk].
    - **Remediation:** [The corrected, secure code block].
3.  If you find absolutely no vulnerabilities, you MUST respond with only this exact phrase and nothing else: `✅ No security issues found in this configuration.`
4.  Do not add any extra conversation or commentary. Your response must be either a list of vulnerabilities or the exact success phrase.

Begin your analysis now.
"""

def create_security_auditor():
    """Initializes and returns an InferenceClient for security auditing."""
    print(f"🤖 Initializing AI security auditor with remote model: {MODEL_ID}...")
    auditor = InferenceClient()
    print("✅ AI security auditor initialized successfully.")
    return auditor

# Post a comment on a PR
def post_pr_comment(analysis_result, filepath):
    """Posts the audit findings as a comment on the relevant pull request."""
    try:
        if not all([GITHUB_TOKEN, REPO_NAME, EVENT_PATH]):
            print("INFO: Not a GitHub Action environment. Skipping PR comment.")
            return

        with open(EVENT_PATH, 'r') as f:
            event_data = json.load(f)
        
        if 'pull_request' not in event_data:
            print("INFO: Not a pull request event. Skipping PR comment.")
            return
            
        pr_number = event_data['pull_request']['number']

        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        pull_request = repo.get_pull(pr_number)
        
        comment = f"### 🤖 AI Security Audit Results\n\n**File:** `{filepath}`\n\n---\n\n{analysis_result}"
        
        pull_request.create_issue_comment(comment)
        print(f"✅ Successfully posted comment to Pull Request #{pr_number}.")

    except Exception as e:
        print(f"❌ Failed to post PR comment: {e}")


def main():
    """Main function to parse arguments and run the security audit."""
    parser = argparse.ArgumentParser(description="AI-powered Terraform Security Auditor.")
    parser.add_argument("path", help="Path to the Terraform file or directory to audit.")
    args = parser.parse_args()

    terraform_files = []
    # Check if the provided path is a directory or a single file
    if os.path.isdir(args.path):
        print(f"🔍 Auditing directory: {args.path}...")
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(".tf"):
                    terraform_files.append(os.path.join(root, file))
    elif os.path.isfile(args.path) and args.path.endswith(".tf"):
        print(f"🔍 Auditing single file: {args.path}...")
        terraform_files.append(args.path)

    if not terraform_files:
        print("No Terraform files found to audit in the specified path.")
        sys.exit(0)

    vulnerabilities_found = False
    auditor = create_security_auditor()

    # Loop through all found Terraform files
    for filepath in terraform_files:
        print(f"\n--- Analyzing '{filepath}' ---")
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                full_terraform_code = file.read()
            
            if not full_terraform_code.strip():
                print("File is empty. Skipping analysis.")
                continue

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_terraform_code}
            ]
            
            print("🤖 Sending request to remote AI model...")
            
            response = auditor.chat_completion(
                model=MODEL_ID,
                messages=messages,
                max_tokens=2048
            )
            
            analysis_result = response.choices[0].message.content.strip()

            if analysis_result:
                print(f"Security Analysis Result for '{filepath}':\n{analysis_result}")
                if "✅ No security issues found" not in analysis_result:
                    vulnerabilities_found = True
            else:
                print("⚠️ Warning: Empty response from AI model.")

        except Exception as e:
            print(f"An unexpected error occurred while processing {filepath}: {e}")
            vulnerabilities_found = True

    # Final check
    if vulnerabilities_found:
        print("\n\n❌ Security vulnerabilities detected. Failing the check.")
        sys.exit(1)
    else:
        print("\n\n✅ No security vulnerabilities detected. Check passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()