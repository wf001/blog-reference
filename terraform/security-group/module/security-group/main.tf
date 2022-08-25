resource "aws_security_group" "this" {
  name   = var.sg_name
  vpc_id = var.vpc

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.sg_name
  }
}

resource "aws_security_group_rule" "from_sg" {
  count                    = length(var.rules_src_sg)
  type                     = "ingress"
  from_port                = element(var.rules_src_sg, count.index).port
  to_port                  = element(var.rules_src_sg, count.index).port
  protocol                 = element(var.rules_src_sg, count.index).protocol
  source_security_group_id = element(var.rules_src_sg, count.index).src_sg
  security_group_id        = aws_security_group.this.id
}

resource "aws_security_group_rule" "from_cidr" {
  count             = length(var.rules_src_cidr)
  type              = "ingress"
  from_port         = element(var.rules_src_cidr, count.index).port
  to_port           = element(var.rules_src_cidr, count.index).port
  protocol          = element(var.rules_src_cidr, count.index).protocol
  cidr_blocks       = element(var.rules_src_cidr, count.index).src_cidr_blocks
  security_group_id = aws_security_group.this.id
}
