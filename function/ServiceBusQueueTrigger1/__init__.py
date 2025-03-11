import logging
import psycopg2
from azure.functions import ServiceBusMessage
from azure.communication.email import EmailClient
from os import getenv

def main(msg: ServiceBusMessage):
    
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 msg.get_body().decode('utf-8'))
    
    notification_id = msg.get_body().decode('utf-8')
    conn_params = {
        'dbname': 'techconfdb',
        'user': getenv('POSTGRES_USER'),
        'password': getenv('POSTGRES_PW'),
        'host': 'projectapp-postgresql.postgres.database.azure.com',
        'port': '5432'
    }

    try:
        # Connect to the database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Query to get notification details
        cursor.execute("SELECT subject, message FROM notification WHERE id = %s", (notification_id,))
        notification = cursor.fetchone()
        if not notification:
            logging.error('Notification with id %s not found', notification_id)
            return

        # Query to get attendees
        cursor.execute("SELECT email, first_name FROM attendee")
        attendees = cursor.fetchall()

        # Loop through each attendee and send a personalized message
        for attendee in attendees:
            subject = '{}: {}'.format(attendee[1], notification[0])
            send_email(attendee[0], subject, notification[1])
            logging.info('Sending email to %s with subject %s', attendee[1], subject)

        # Update the notification status
        cursor.execute("UPDATE notification SET status = %s, completed_date = NOW() WHERE id = %s",
                       ('Completed',  notification_id))
        conn.commit()

    except Exception as e:
        logging.error('Error processing notification: %s', str(e))
    finally:
        cursor.close()
        conn.close()


def send_email(email, subject, body):
    try:
        connection_string = getenv('AZUREMAILER_API_KEY')
        client = EmailClient.from_connection_string(connection_string)
        from_email= getenv('ADMIN_EMAIL_ADDRESS')
      
        message = {
            "senderAddress": from_email,
            "recipients": {
                "to": [{"address": email}]
            },
            "content": {
                "subject": subject,
                "plainText": body
            },
            
        }
        poller = client.begin_send(message)
        result = poller.result()
        print("Message sent: ", result)

    except Exception as ex:
        print(ex)