# Cloud Native Project With DevOps and GitOps

## Goal

![Goal](https://miro.medium.com/max/700/1*0MpcMgFb4hkcqXtflGSYNQ.png)

## Prerequisite

- poetry >= 1.1.13
- python >= 3.8
  - pre-commit >= 2.20.0

## Installation

### User Service

```Bash
# Clone Repository
git clone https://github.com/jungmir/msa_template.git

# Move into project
cd msa_template/User

# install application dependencies
## using poetry
poetry check && poetry install

## using pip3
pip3 install -r requirements/requirements.txt
```

### Build and Run

```Bash
# build
sh build.sh

# run
sh run.sh
```

## Reference

- [Goal Image](https://blog.argoproj.io/introducing-argo-cd-declarative-continuous-delivery-for-kubernetes-da2a73a780cd)
- [pre-commit](https://pre-commit.com/)
- [argoCD](https://argo-cd.readthedocs.io/en/stable/)
- [Github Actions](https://github.com/features/actions)
