data "aws_ssm_parameter" "this" {
  name = var.ssm_token_parameter_name
}

resource "aws_codebuild_source_credential" "this" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB"
  token       = data.aws_ssm_parameter.this.value
}

resource "aws_codebuild_project" "this" {
  name         = var.build_prj_name
  service_role = var.role
  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "aws/codebuild/standard:3.0"
    type         = "LINUX_CONTAINER"
  }
  artifacts {
    type = "NO_ARTIFACTS"

  }
  logs_config {
    cloudwatch_logs {
      status = "ENABLED"
    }
  }
  source {
    type            = "GITHUB"
    location        = var.repo
    git_clone_depth = 1
    buildspec       = file("../../module/codebuild/buildspec.yml")
  }
}
resource "aws_codebuild_webhook" "this" {
  project_name = aws_codebuild_project.this.name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PUSH"
    }

    filter {
      type    = "HEAD_REF"
      pattern = "^refs/heads/${var.branch_name}$"
    }
  }
  depends_on = [
    aws_codebuild_source_credential.this
  ]
}
