import argparse
import os
import hcl2
import json
import sys
from huggingface_hub import InferenceClient

# Configuration
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

SYSTEM_PROMPT = """You are an expert security auditor for Terraform code. Your task is to analyze the provided Terraform resource and identify any security vulnerabilities based on industry best practices. Your analysis must be strict and accurate.

**Rules:**
1.  Analyze ONLY the provided Terraform code block. Do not assume other resources exist.
2.  If you find one or more vulnerabilities, your response MUST follow this exact format for each one:
    - **Vulnerability:** A one-sentence summary and its severity (CRITICAL, HIGH, MEDIUM, LOW).
    - **Risk:** A brief explanation of the security risk.
    - **Remediation:** The corrected, secure code block.
3.  If, and only if, you find absolutely no vulnerabilities, you MUST respond with only this exact phrase and nothing else: `✅ No security issues found in this configuration.`
4.  Do not add any extra conversation, commentary, or recommendations for "best practices" if no direct vulnerability is found in the provided code.

Begin your analysis now.
"""

# Create the auditor
def create_security_auditor():
    """Initializes and returns an InferenceClient for security auditing."""
    print(f"🤖 Initializing AI security auditor with remote model: {MODEL_ID}...")
    
    # The token is read automatically from the HUGGING_FACE_HUB_TOKEN environment variable
    auditor = InferenceClient()
    
    print("✅ AI security auditor initialized successfully.")
    return auditor

def format_terraform_resource(resource_type, resource_name, resource_body):
    """Formats a Terraform resource with proper HCL syntax."""
    def format_block(block, indent_level=0):
        lines = []
        indent = "  " * indent_level
        for key, value in block.items():
            if isinstance(value, list) and all(isinstance(i, dict) for i in value):
                for item in value:
                    lines.append(f'{indent}{key} {{')
                    lines.extend(format_block(item, indent_level + 1))
                    lines.append(f'{indent}}}')
            else:
                lines.append(f'{indent}{key} = {json.dumps(value)}')
        return lines

    lines = [f'resource "{resource_type}" "{resource_name}" {{']
    lines.extend(format_block(resource_body, 1))
    lines.append('}')
    return '\n'.join(lines)

def main():
    """Main function to parse arguments and run the security audit."""
    parser = argparse.ArgumentParser(description="AI-powered Terraform Security Auditor.")
    parser.add_argument("filepath", help="Path to the Terraform (.tf) file to audit.")
    args = parser.parse_args()

    print(f"🔍 Auditing {args.filepath}...")
    vulnerabilities_found = False

    try:
        # Read the entire file content into one string
        with open(args.filepath, 'r', encoding='utf-8') as file:
            full_terraform_code = file.read()

        auditor = create_security_auditor()

        # Format the prompt for the entire file
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_terraform_code}
        ]
        
        print("\n--- Analyzing full file content ---")
        print("🤖 Sending request to remote AI model...")
        
        # Send the entire file content in a single API call
        response = auditor.chat_completion(
            model=MODEL_ID,
            messages=messages,
            max_tokens=2048
        )
        
        analysis_result = response.choices[0].message.content.strip()

        if analysis_result:
            print(f"Security Analysis Result:\n{analysis_result}")
            if "✅ No security issues found" not in analysis_result:
                vulnerabilities_found = True
        else:
            print("⚠️ Warning: Empty response from AI model.")

    except FileNotFoundError:
        print(f"Error: The file '{args.filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    # Final check
    if vulnerabilities_found:
        print("\n\n❌ Security vulnerabilities detected. Failing the check.")
        sys.exit(1)
    else:
        print("\n\n✅ No security vulnerabilities detected. Check passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()