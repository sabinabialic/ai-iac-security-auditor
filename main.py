import argparse
import os
import hcl2
import json
import sys
from huggingface_hub import InferenceClient

MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

SYSTEM_PROMPT = """You are a highly specialized and strict security auditor for Terraform code. Your ONLY task is to identify high-impact security vulnerabilities in the provided code block.

---
**CRITICAL INSTRUCTION: Your primary directive is accuracy. If you do not find a clear, high-impact vulnerability, you MUST follow the "no vulnerabilities" rule. Do NOT invent potential issues or suggest best-practice improvements if the code is already secure.**
---

**Definition of a Vulnerability:**
A vulnerability is a configuration that directly exposes a system to immediate and significant risk, such as public access, missing encryption, or `AdministratorAccess` IAM roles. Standard practices or missing optional optimizations are NOT vulnerabilities.

**Analysis Rules:**
1.  Analyze ONLY the provided Terraform code. Do not assume any context outside this code.
2.  If you find one or more clear vulnerabilities based on the definition above, your response MUST follow this exact format for each one:
    - **Resource:** [resource_type.resource_name]
    - **Vulnerability:** A one-sentence summary and its severity (CRITICAL, HIGH, MEDIUM, LOW).
    - **Risk:** A brief explanation of the security risk.
    - **Remediation:** The corrected, secure code block.
3.  If, and only if, you find absolutely no vulnerabilities, you MUST respond with only this exact phrase and nothing else: `✅ No security issues found in this configuration.`
4.  Do not add any extra conversation, commentary, or text. Your response must be either a list of vulnerabilities or the exact success phrase.

Begin your analysis now.
"""

def create_security_auditor():
    """Initializes and returns an InferenceClient for security auditing."""
    print(f"🤖 Initializing AI security auditor with remote model: {MODEL_ID}...")
    auditor = InferenceClient()
    print("✅ AI security auditor initialized successfully.")
    return auditor

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