import argparse
import os
import hcl2
import json
from huggingface_hub import InferenceClient

# Configuration
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

SYSTEM_PROMPT = """You are an expert security auditor for Terraform code. Your task is to analyze the provided Terraform resource and identify any security vulnerabilities based on industry best practices.

Look for common misconfigurations, including but not limited to:
- Unrestricted network access (e.g., security group ingress from "0.0.0.0/0").
- Publicly exposed storage buckets.
- Missing encryption on resources like S3 buckets or EBS volumes.
- Hardcoded secrets or sensitive credentials.
- Overly permissive IAM roles and policies.

For each vulnerability you find, you must provide the following information in a clear, structured format using Markdown:
- Vulnerability: A one-sentence summary of the issue and its severity (CRITICAL, HIGH, MEDIUM, LOW).
- Risk: A brief explanation of why this configuration is a security risk.
- Remediation: The corrected, secure code block that mitigates the vulnerability.

If you find no vulnerabilities, you must respond with only this exact phrase:
✅ No security issues found in this configuration.
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

    try:
        with open(args.filepath, 'r', encoding='utf-8') as file:
            tf_data = hcl2.load(file)

        auditor = create_security_auditor()

        if 'resource' in tf_data:
            for resource_block in tf_data['resource']:
                for resource_type, resource_config in resource_block.items():
                    for resource_name, resource_body in resource_config.items():
                        print(f"\n--- Analyzing resource: {resource_type}.{resource_name} ---")
                        
                        if isinstance(resource_body, list) and resource_body:
                            resource_body = resource_body[0]
                        
                        resource_code = format_terraform_resource(resource_type, resource_name, resource_body)
                        
                        # Format the prompt for a chat/conversational model
                        messages = [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": resource_code}
                        ]
                        
                        print("🤖 Sending request to remote AI model...")
                        
                        # Use the chat_completion method for instruction-tuned models
                        response = auditor.chat_completion(
                            model=MODEL_ID,
                            messages=messages,
                            max_tokens=1024
                        )
                        
                        # Extract the generated text from the response object
                        analysis_result = response.choices[0].message.content.strip()

                        if analysis_result:
                            print(f"Security Analysis Result:\n{analysis_result}")
                        else:
                            print("⚠️ Warning: Empty response from AI model.")

    except FileNotFoundError:
        print(f"Error: The file '{args.filepath}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()