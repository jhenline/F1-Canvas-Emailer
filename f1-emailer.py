# Jeff Henline / 2023-11-16
# Script was created for F-1 Mandatory Workshop
# 
# Script checks for new quiz submissions since the last run and 
# sends an email with the list of students who submitted the quiz.

import requests
import datetime
import os
from dateutil import parser
import pytz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the config.ini file
config.read('/home/bitnami/scripts/config.ini')


# Canvas API details
canvas_api_url = 'https://calstatela.instructure.com/api/v1/'
access_token = config['auth']['token']

# SendGrid API details
sg = SendGridAPIClient(config['auth']['sendgrid_api_key'])

# Course and quiz details
course_id = '94338'
quiz_id = '410870'

# File to store the last run time
last_run_file = '/home/bitnami/scripts/canvas/F1-Emailer/last_run.txt'

# Timezone for PST
pst = pytz.timezone('America/Los_Angeles')

# Sends an email with the given subject and content using SendGrid.
def send_email(subject, content):
    # Construct the email
    # recipients = ['henlij@gmail.com']
    recipients = ['international@calstatela.edu', 'jhenlin2@calstatela.edu']
    message = Mail(
        from_email='cetltech@calstatela.edu',
        to_emails=recipients,
        subject=subject,
        html_content=content
    )

    # Send the email
    try:
        response = sg.send(message)
        print(f"Email sent with status code: {response.status_code}")
    except Exception as e:
        print(e)

# Reads the last run time from a file. If the file doesn't exist or is empty, it returns None.
def get_last_run_time():
    if not os.path.exists(last_run_file):
        print("Last run file does not exist. Creating file for the first run.")
        with open(last_run_file, 'w') as file:
            current_time = datetime.now().astimezone(pst)
            file.write(current_time.isoformat())
        return None

    with open(last_run_file, 'r') as file:
        last_run_time_str = file.read().strip()
        if not last_run_time_str:
            print("Last run file is empty. This might be the first run.")
            return None
        return parser.isoparse(last_run_time_str).astimezone(pst)


# Writes the current time (in PST) to the file storing the last run time.
def update_last_run_time():
    with open(last_run_file, 'w') as file:
        # Store current time in PST
        file.write(datetime.datetime.now(pst).isoformat())


# Fetches user details (name and email) from Canvas API for a given user ID.
def get_user_details(user_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{canvas_api_url}users/{user_id}', headers=headers)
    user = response.json()
    return user.get('name'), user.get('email')


# Retrieves quiz submissions from the Canvas API. 
def get_quiz_submissions(since_time=None):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'per_page': 100}
    if since_time:
        # Convert since_time back to UTC before making the request
        params['submitted_since'] = since_time.astimezone(pytz.utc).isoformat()

    student_submissions = []
    url = f'{canvas_api_url}courses/{course_id}/quizzes/{quiz_id}/submissions'
    assignment_id = '1562953'
    while url:
        response = requests.get(url, headers=headers, params=params)
        submissions = response.json()
        for submission in submissions.get('quiz_submissions', []):
            finished_at = submission.get('finished_at')
            if finished_at:
                submitted_at = parser.isoparse(finished_at).astimezone(pst)
                if not since_time or submitted_at > since_time:
                    user_id = submission['user_id']
                    name, email = get_user_details(user_id)
                    # Correct the quiz attempt URL
                    quiz_attempt_url = f"https://calstatela.instructure.com/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&student_id={user_id}"
                    student_info = {
                        'user_id': user_id,
                        'name': name,
                        'email': email,
                        'score': submission['score'],
                        'quiz_attempt_url': quiz_attempt_url  # Add the URL here
                    }
                    student_submissions.append(student_info)

        url = response.links['next']['url'] if 'next' in response.links else None
        params = {}

    return student_submissions


last_run_time = get_last_run_time()
print(f"Last run time: {last_run_time}")
student_submissions = get_quiz_submissions(last_run_time)
update_last_run_time()

# Prepare email content
if last_run_time:
    subject = f"Quiz Submissions Report for F-1 Mandatory Workshop"

    if student_submissions:
        content = f"<p>Students who submitted the quiz since the last run on {last_run_time.strftime('%Y-%m-%d %H:%M:%S')} (PST):</p><ul>"
        for submission in student_submissions:
            content += f"<li>User ID: {submission['user_id']}, Name: {submission['name']}, Email: {submission['email']}, Score: {submission['score']}, <a href='{submission['quiz_attempt_url']}'>Quiz Attempt</a></li>"
        content += "</ul>"
    else:
        content = f"<p>No new quiz submissions since the last run on {last_run_time.strftime('%Y-%m-%d %H:%M:%S')} (PST).</p>"
else:
    subject = "Quiz Submissions Report"
    content = "<p>Unable to determine the last run time.</p>"

# Send the email
send_email(subject, content)
