# Vulnerability: Publicly accessible S3 bucket
resource "aws_s3_bucket" "insecure_user_uploads" {
  bucket = "my-insecure-public-bucket-67890"
  acl    = "public-read" # This makes the bucket public

  tags = {
    Name = "Insecure Public Bucket"
  }
}

# Vulnerability: Unrestricted security group ingress
resource "aws_security_group" "allow_all_traffic" {
  name        = "allow_all_sg"
  description = "Allow all inbound traffic from anywhere"

  ingress {
    description = "Allow all ports and protocols"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Vulnerability: Overly permissive IAM role
resource "aws_iam_role" "admin_access_role" {
  name = "iam-role-with-full-admin-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "admin_policy_attachment" {
  role       = aws_iam_role.admin_access_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess" # Grants full admin rights
}