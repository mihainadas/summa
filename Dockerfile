FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=galandriel.settings

# Set work directory
WORKDIR /summa
COPY . /summa

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/summa/entrypoint.sh"]
