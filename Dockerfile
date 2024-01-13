FROM python

# Copy app files
COPY . /usr/app
WORKDIR /usr/app

# Install dependencies
RUN pip install -r requirements.txt

# Run Battlesnake
CMD [ "python", "main.py" ]
