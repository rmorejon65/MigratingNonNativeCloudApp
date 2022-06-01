import logging
import azure.functions as func
import psycopg2
import os
import json
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime as dt

def send_email(email, subject, body):
    if not os.environ['SENDGRID_API_KEY']:
        message = Mail(
            from_email=os.environ['ADMIN_EMAIL_ADDRESS'],
            to_emails=email,
            subject=subject,
            plain_text_content=body)

        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        sg.send(message)

def main(msg: func.ServiceBusMessage):

    msgReceived = msg.get_body().decode('utf-8')
    logging.info("entering the trigger")
    result = json.dumps({
        'message_id': msg.message_id,
        'body': msg.get_body().decode('utf-8'),
        'content_type': msg.content_type,
        'expiration_time': msg.expiration_time,
        'label': msg.label,
        'partition_key': msg.partition_key,
        'reply_to': msg.reply_to,
        'reply_to_session_id': msg.reply_to_session_id,
        'scheduled_enqueue_time': msg.scheduled_enqueue_time,
        'session_id': msg.session_id,
        'time_to_live': msg.time_to_live,
        'to': msg.to,
        'user_properties': msg.user_properties,
        'metadata' : msg.metadata
    }, default=str)
    logging.info(result)
    logging.info(msgReceived)
    notification_id = int(msgReceived)
    logging.info(msgReceived)
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(os.environ["POSTGRES_URL"],os.environ["POSTGRES_USER"],os.environ["POSTGRES_DB"],os.environ["POSTGRES_PW"],"require")
    
    
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        logging.info("cursor open")
        # TODO: Get notification message and subject from database using the notification_id
        cursor.execute("Select subject, message FROM notification where id  = %s;", (notification_id,))
        notificationInfo = cursor.fetchone()
        logging.info("notification was found")
        # TODO: Get attendees email and name
        cursor.execute("select email, first_name, last_name FROM attendee")
        attendees = cursor.fetchall()
        logging.info("processing all attendees")
        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            subject = '{} {}: {}'.format(attendee[1], attendee[2], notificationInfo[0])
            logging.info(subject)
            send_email(attendee[0], subject, notificationInfo[1])           
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        status = 'Notified : {} attendees '.format(len(attendees))
        logging.info(status)
        cursor.execute("UPDATE notification SET completed_date = %s, status = %s WHERE id = %s;", (datetime.today(), status, notification_id))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        cursor.close()
        conn.close()

