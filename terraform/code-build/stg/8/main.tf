provider "aws" {
  region = "ap-northeast-1"
}
module "codebuild" {
  source                   = "../../module/codebuild"
  role                     = var.codebuild_service_role_arn
  repo                     = var.repo_url
  ssm_token_parameter_name = var.ssm_token_parameter_name
  build_prj_name = var.build_prj_name
  branch_name = var.branch_name
}
