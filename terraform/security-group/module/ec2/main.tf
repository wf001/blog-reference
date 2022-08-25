resource "aws_instance" "this" {
  ami = "ami-00f17260d61953f3f"
  instance_type = "t3.micro"
  subnet_id       = "subnet-024fbdf3207df0904"
  security_groups = var.sg_ids
}
