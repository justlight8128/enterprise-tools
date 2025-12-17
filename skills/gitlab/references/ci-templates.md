# GitLab CI/CD Templates

## Basic Pipeline

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - npm install
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  script:
    - npm test

deploy:
  stage: deploy
  script:
    - echo "Deploying..."
  only:
    - main
```

## Python Project

```yaml
image: python:3.11

stages:
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/
    - venv/

before_script:
  - python -m venv venv
  - source venv/bin/activate
  - pip install -r requirements.txt

test:
  stage: test
  script:
    - pytest --cov=src tests/
  coverage: '/TOTAL.*\s+(\d+%)$/'

lint:
  stage: test
  script:
    - ruff check src/
    - mypy src/

build:
  stage: build
  script:
    - pip wheel . -w dist/
  artifacts:
    paths:
      - dist/
```

## Node.js Project

```yaml
image: node:20

stages:
  - install
  - test
  - build
  - deploy

cache:
  paths:
    - node_modules/

install:
  stage: install
  script:
    - npm ci
  artifacts:
    paths:
      - node_modules/

test:
  stage: test
  script:
    - npm test
  needs:
    - install

lint:
  stage: test
  script:
    - npm run lint
  needs:
    - install

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
  needs:
    - test
    - lint
```

## Docker Build

```yaml
build-image:
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_TLS_CERTDIR: ""
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - |
      if [ "$CI_COMMIT_BRANCH" = "main" ]; then
        docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
        docker push $CI_REGISTRY_IMAGE:latest
      fi
```

## Multi-Environment Deploy

```yaml
.deploy_template: &deploy
  script:
    - echo "Deploying to $ENV..."
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy-staging:
  <<: *deploy
  stage: deploy
  variables:
    ENV: staging
  environment:
    name: staging
  only:
    - develop

deploy-production:
  <<: *deploy
  stage: deploy
  variables:
    ENV: production
  environment:
    name: production
  only:
    - main
  when: manual
```

## Useful Variables

| Variable | Description |
|----------|-------------|
| `CI_COMMIT_SHA` | Full commit SHA |
| `CI_COMMIT_SHORT_SHA` | Short SHA (8 chars) |
| `CI_COMMIT_BRANCH` | Branch name |
| `CI_COMMIT_TAG` | Tag name |
| `CI_PROJECT_NAME` | Project name |
| `CI_REGISTRY_IMAGE` | Container registry path |
| `CI_PIPELINE_ID` | Pipeline ID |
| `CI_JOB_ID` | Job ID |

## Tips

1. Use `needs:` for parallel execution
2. Cache dependencies
3. Use `artifacts:expire_in` to save storage
4. Use `rules:` instead of `only/except` (newer syntax)
