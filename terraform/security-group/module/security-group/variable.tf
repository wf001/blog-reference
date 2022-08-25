//Name
variable "sg_name" {}

//Network
variable "vpc" {}

//Secritu Group Rule definition of Inboud from Security Group
variable "rules_src_sg" {}
//Secritu Group Rule definition of Inboud from Specified Cidr Block
variable "rules_src_cidr" {}
