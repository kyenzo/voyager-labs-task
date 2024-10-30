provider "aws" {
  region = "eu-central-1"  # Adjust to your preferred region
}

variable "instance_type" {
  default = "t2.small"
}

variable "centos_ami_id" {
  default = "ami-0fc80b3f088841e60"  # Replace with the exact CentOS AMI ID
}

variable "key_name" {
  default = "main-key"  # Specify the name of the SSH key in AWS
}

# Security Group for SSH access
resource "aws_security_group" "ec2_sg" {
  name        = "ec2-ssh-sg"
  description = "Allow SSH access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance with user_data to configure 'dev' user SSH access
resource "aws_instance" "ec2_instance" {
  count                  = 2
  ami                    = var.centos_ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name  # Use "main-key.pem" for initial connection
  security_groups        = [aws_security_group.ec2_sg.name]

  tags = {
    Name = "DevOpsInstance-${count.index + 1}"
  }

  # User data to create 'dev' user and set up SSH access
  user_data = <<-EOF
    #!/bin/bash
    # Update system packages
    sudo yum update -y

    # Create 'dev' user and set up SSH access
    sudo useradd -m -s /bin/bash dev
    sudo mkdir -p /home/dev/.ssh

    # Copy the authorized_keys from ec2-user to dev user for shared SSH access
    sudo cp /home/ec2-user/.ssh/authorized_keys /home/dev/.ssh/authorized_keys

    # Set ownership and permissions for the dev user
    sudo chown -R dev:dev /home/dev/.ssh
    sudo chmod 700 /home/dev/.ssh
    sudo chmod 600 /home/dev/.ssh/authorized_keys

    # Format and mount volumes
    if [ -e /dev/xvdf ]; then
        sudo mkfs -t ext4 /dev/xvdf
        sudo mkdir -p /data
        echo '/dev/xvdf /data ext4 defaults 0 0' | sudo tee -a /etc/fstab
        sudo mount /data
    fi

    if [ -e /dev/xvdg ]; then
        sudo mkfs -t ext4 /dev/xvdg
        sudo mkdir -p /data1
        echo '/dev/xvdg /data1 ext4 defaults 0 0' | sudo tee -a /etc/fstab
        sudo mount /data1
    fi
  EOF


}


# Elastic IP for each instance
resource "aws_eip" "ec2_eip" {
  count      = 2
  instance   = aws_instance.ec2_instance[count.index].id
  depends_on = [aws_instance.ec2_instance]
}

# Attach 1GB Volumes to each instance with specified availability zone
resource "aws_ebs_volume" "data_volume_1" {
  count             = 2
  size              = 1
  type              = "gp2"
  availability_zone = aws_instance.ec2_instance[count.index].availability_zone
  tags = {
    Name = "DataVolume1-${count.index + 1}"
  }
}

resource "aws_ebs_volume" "data_volume_2" {
  count             = 2
  size              = 1
  type              = "gp2"
  availability_zone = aws_instance.ec2_instance[count.index].availability_zone
  tags = {
    Name = "DataVolume2-${count.index + 1}"
  }
}

# Attach Volumes to Instances
resource "aws_volume_attachment" "attach_volume_data1" {
  count        = 2
  device_name  = "/dev/xvdf"
  volume_id    = aws_ebs_volume.data_volume_1[count.index].id
  instance_id  = aws_instance.ec2_instance[count.index].id
  depends_on   = [aws_instance.ec2_instance]
}

resource "aws_volume_attachment" "attach_volume_data2" {
  count        = 2
  device_name  = "/dev/xvdg"
  volume_id    = aws_ebs_volume.data_volume_2[count.index].id
  instance_id  = aws_instance.ec2_instance[count.index].id
  depends_on   = [aws_instance.ec2_instance]
}
