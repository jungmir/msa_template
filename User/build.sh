docker build --build-arg PORT=8888 --build-arg ENV=prod -f ./docker/dockerfile . --tag base_image