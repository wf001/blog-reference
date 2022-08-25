provider "aws" {
  region = "ap-northeast-1"
}

module "ec2" {
    source = "../../module/ec2"
    sg_ids = [module.ec2-sg.sg_id]
}

module "ec2-sg" {
  source = "../../module/security-group"
  vpc    = var.vpc
  sg_name = "ec2-sg"
  rules_src_sg = ([])
  rules_src_cidr = ([
    {
      src_cidr_blocks   = ["10.0.0.0/16"]
      port     = 80
      protocol = "tcp"
    },
    {
      src_cidr_blocks   = ["10.1.0.0/16"]
      port     = 80
      protocol = "tcp"
    }
])
}
