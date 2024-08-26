# F-1 Mandatory Workshop Quiz Submission Checker

## Overview

This script is designed to assist in managing the F-1 Mandatory Workshop by checking for new quiz submissions in a Canvas course. The script tracks the last time it was run and sends an email containing a list of students who have submitted the quiz since that time.

## Features

- **Tracks Quiz Submissions:** The script fetches quiz submissions from Canvas and compares them with the last recorded run time to identify new submissions.
- **Email Notification:** An email is sent to specified recipients with the details of students who have submitted the quiz, including their name, email, score, and a link to their quiz attempt.
- **Error Handling:** Basic error handling is implemented for API requests and email sending.

## Prerequisites

- Python 3.7 or higher
- The following Python libraries:
  - `requests`
  - `dateutil`
  - `pytz`
  - `sendgrid`
  - `configparser`
- A Canvas API token with the necessary permissions to access quiz submissions.
- A SendGrid API key for sending emails.
- A configured `config.ini` file with the following sections:

  ```ini
  [auth]
  token = your_canvas_api_token
  sendgrid_api_key = your_sendgrid_api_key
