# Cranio_Norm

## Description

A Django web application that allows the user to input skull models in PLY file format. User is able to select anatomical points which will be used to output a normalized skull model in PLY file format.

## Instructions

- Clone the repository from the develop branch.
- Create a new conda enviroment.
  - `conda create --name ENV_NAME python`
- Activiate new conda enviroment.
  - `conda activate ENV_NAME`
- Navigate to the base of the project in the conda terminal.
- Execute `pip install -r requirements.txt`
- Execute `python manage.py makemigrations`
- Execute `python manage.py migrate`
- Start the server by executing `python manage.py runserver`
- Open brower
  - EX) http://127.0.0.1:8000/cranio/home/
