[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/18vkNgfz)
<br/>Arib Amin
<br/>Jennifer Wang
<br/>Dricmoy Bhattacharjee
<br/>Fairuz Zarif
<br/>Jaden Huang
<br/>Jiahao Li

# Lavender Project - Local Setup & Test Instructions

### Find our API documentation [here]( https://[2605:fd00:4:1001:f816:3eff:fe7d:b637]/api/docs/).

### Running Instance Available [here]( https://[2605:fd00:4:1001:f816:3eff:fe7d:b637]/).

---
## **Steps to run locally**
1. Initialize a venv envrionment with "python -m venv venv"
2. Activate the env with "source venv/bin/activate" then install the dependencies with "pip install -r requirements.txt"
3. make a .env file in the source directory with LOCAL_HOST="http://127.0.0.1:8000/"
4. cd into the source directory, run "python manage.py makemigrations", "python manage.py migrate" & "python manage.py runserver"


## **Steps to Run Locally**
1. Follow steps 1-3 for local, except change the environment key in .env to LOCAL_HOST="http://testserver/"
2. cd into the source directory, run "python manage.py makemigrations", "python manage.py migrate" if you haven't
3. Launch the tests with "python manage.py test"
