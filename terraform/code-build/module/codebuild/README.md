## 
``` buildspec.yml
version: 0.2

phases:
    build:
        commands:
            - cd ..
            - zip -r rails-test.zip rails-test
            - aws s3 cp hoge.zip s3://hoge-bucket

```
