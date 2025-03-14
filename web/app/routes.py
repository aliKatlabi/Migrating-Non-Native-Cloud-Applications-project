from app import app, db, queue_client
from datetime import datetime
from app.models import Attendee, Conference, Notification
from flask import render_template, session, request, redirect, url_for, flash, make_response, session
import logging
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from os import getenv

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/Registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        attendee = Attendee()
        attendee.first_name = request.form['first_name']
        attendee.last_name = request.form['last_name']
        attendee.email = request.form['email']
        attendee.job_position = request.form['job_position']
        attendee.company = request.form['company']
        attendee.city = request.form['city']
        attendee.state = request.form['state']
        attendee.interests = request.form['interest']
        attendee.comments = request.form['message']
        attendee.conference_id = app.config.get('CONFERENCE_ID')

        try:
            db.session.add(attendee)
            db.session.commit()
            session['message'] = 'Thank you, {} {}, for registering!'.format(attendee.first_name, attendee.last_name)
            return redirect('/Registration')
        except:
            logging.error('Error occured while saving your information')

    else:
        if 'message' in session:
            message = session['message']
            session.pop('message', None)
            return render_template('registration.html', message=message)
        else:
             return render_template('registration.html')

@app.route('/Attendees')
def attendees():
    attendees = Attendee.query.order_by(Attendee.submitted_date).all()
    return render_template('attendees.html', attendees=attendees)


@app.route('/Notifications')
def notifications():
    notifications = Notification.query.order_by(Notification.id).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/Notification', methods=['POST', 'GET'])
def notification():
    if request.method == 'POST':
        notification = Notification()
        notification.message = request.form['message']
        notification.subject = request.form['subject']
        notification.status = 'Notifications submitted'
        notification.submitted_date = datetime.utcnow()

        try:
            db.session.add(notification)
            db.session.commit()
            
            notification.completed_date = datetime.utcnow()
            attendees = Attendee.query.all()
            notification.status = 'Notified {} attendees'.format(len(attendees))
            db.session.commit()

            #  Call servicebus queue_client to enqueue notification ID

            
            asyncio.run(send(str(notification.id)))

            return redirect('/Notifications')
        except Exception as e:
            logging.error(f'Unable to save notification: {e}')
            return render_template('notification.html', error='An error occurred while saving the notification.')
          

    else:
        return render_template('notification.html')



async def send_single_message(sender,massage):
    # Create a Service Bus message and send it to the queue
    message_ = ServiceBusMessage(massage)
    await sender.send_messages(message_)
    print("Sent a single message")

async def send(massage):
    # create a Service Bus client using the connection string
    async with ServiceBusClient.from_connection_string(
        conn_str=getenv('SERVICE_BUS_CONNECTION_STRING'),
        logging_enable=True) as servicebus_client:
        # Get a Queue Sender object to send messages to the queue
        sender = servicebus_client.get_queue_sender(queue_name=getenv('SERVICE_BUS_QUEUE_NAME'))
        async with sender:
            # Send one message
            await send_single_message(sender,massage)
            # Send a list of messages
            # await send_a_list_of_messages(sender)
            # Send a batch of messages
            # await send_batch_message(sender)