FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt  .
# install dependencies
RUN  pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}
ADD library ${LAMBDA_TASK_ROOT}/library/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.lambda_handler" ]