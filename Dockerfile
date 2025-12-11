FROM public.ecr.aws/lambda/python:3.11

# Copy Lambda function
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Copy requirements if any
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["lambda_function.lambda_handler"]
