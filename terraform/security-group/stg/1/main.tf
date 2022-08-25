provider "aws" {
  region = "ap-northeast-1"
}


########
# 
########
module "sg1" {
  source = "../../module/security-group"
  vpc    = var.vpc
  sg_name = "sg1"
  rules_src_sg = ([
    {
      src_sg   = module.sg2.sg_id
      port     = 80
      protocol = "tcp"
    }
  ])
  rules_src_cidr = ([])
}
module "sg2" {
  source = "../../module/security-group"
  vpc    = var.vpc
  sg_name = "sg2"
  rules_src_sg = ([
    {
      src_sg   = module.sg2.sg_id
      port     = 80
      protocol = "tcp"
    }
  ])
  rules_src_cidr = ([])
}
########
# 
########
module "sg3" {
  source = "../../module/security-group"
  vpc    = var.vpc
  sg_name = "sg3"
  rules_src_sg = ([
    {
      src_sg   = module.sg1.sg_id
      port     = 80
      protocol = "tcp"
    },
    {
      src_sg   = module.sg2.sg_id
      port     = 80
      protocol = "tcp"
    }
  ])
  rules_src_cidr = ([
    {
      src_cidr_blocks = ["10.1.0.0/16"]
      port            = 80
      protocol        = "tcp"
    },
    {
      src_cidr_blocks = ["10.2.0.0/16"]
      port            = 80
      protocol        = "tcp"
    }
  ])
}
