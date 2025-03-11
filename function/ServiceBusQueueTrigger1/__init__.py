import logging
import psycopg2
from azure.functions import ServiceBusMessage

def main(msg: ServiceBusMessage):
    
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 msg.get_body().decode('utf-8'))
    
    notification_id = msg.get_body().decode('utf-8')
    conn_params = {
        'dbname': 'your_db_name',
        'user': 'your_db_user',
        'password': 'your_db_password',
        'host': 'your_db_host',
        'port': 'your_db_port'
    }

    try:
        # Connect to the database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Query to get notification details
        cursor.execute("SELECT subject, message FROM notifications WHERE id = %s", (notification_id,))
        notification = cursor.fetchone()
        if not notification:
            logging.error('Notification with id %s not found', notification_id)
            return

        subject, message = notification

        # Query to get attendees
        cursor.execute("SELECT email, first_name FROM attendees")
        attendees = cursor.fetchall()

        # Loop through each attendee and send a personalized message
        for attendee in attendees:
            email, first_name = attendee
            personalized_message = f"Dear {first_name},\n\n{message}"
            # Here you would send the email using your preferred email service
            logging.info('Sending email to %s with subject %s', email, subject)

        # Update the notification status
        cursor.execute("UPDATE notifications SET status = %s, completed_date = NOW(), attendees_notified = %s WHERE id = %s",
                       ('Completed', len(attendees), notification_id))
        conn.commit()

    except Exception as e:
        logging.error('Error processing notification: %s', str(e))
    finally:
        cursor.close()
        conn.close()