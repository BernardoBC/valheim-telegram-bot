#!/usr/bin/env python3
import datetime
import logging
import sys
import boto3
from config import *
from botocore.exceptions import ClientError
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

#ec2
ec2 = boto3.client('ec2')
ec2resource = boto3.resource('ec2')

updater = Updater(token=telegramToken, use_context=True)

#logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)    

def isPastMidnight():
    time_to_check = datetime.datetime.now().time()
    if time_to_check >= datetime.time(0):
        if time_to_check <= datetime.time(6):
            return True
    return False

def shutdown(update: Update, context: CallbackContext):
    try:
        response = ec2.stop_instances(InstanceIds=[instanceId], DryRun=False)
        print(response)
        user = update.message.from_user
        if(isPastMidnight):
            update.message.reply_text("The server has shutdown. {}, it's past midnight. got to sleep".format(user['username']))
        update.message.reply_text("The server has shutdown.")
    except ClientError as e:
        print(e)
        update.message.reply_text("something failed. Was the server already stopped? regardless, blame Terny.")
        update.message.reply_text(e)

def startup(update: Update, context: CallbackContext):
    try:
        response = ec2.start_instances(InstanceIds=[instanceId], DryRun=False)
        print(response)
        update.message.reply_text("Server has started.")
    except ClientError as e:
        print(e)
        update.message.reply_text("something failed. Was the server up already? regardless, blame Terny.")
        update.message.reply_text(e)

def checkStatus(update: Update, context: CallbackContext):
    instance = ec2resource.Instance(instanceId)
    print (instance.id , instance.state)
    update.message.reply_text(instance.state)

def reboot(update: Update, context: CallbackContext):
    try:
        response = ec2.reboot_instances(InstanceIds=[instanceId], DryRun=False)
        print('Success', response)
        update.message.reply_text("Success. Server rebooted.")
    except ClientError as e:
        print('Error', e)  
        update.message.reply_text(e) 

#todo: update command
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Commands: /startup /shutdown /reboot /checkStatus') 

def main():
    """Start the bot."""
    # Create the Updater and pass the token
    updater = Updater(telegramToken)
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    #commands
    dispatcher.add_handler(CommandHandler("startup", startup))
    dispatcher.add_handler(CommandHandler("shutdown", shutdown))
    dispatcher.add_handler(CommandHandler("checkStatus", checkStatus))
    dispatcher.add_handler(CommandHandler("reboot", reboot))
    dispatcher.add_handler(CommandHandler("help", help_command))
    
    updater.start_polling()
    updater.idle()

#pretty self explanatory
if __name__ == '__main__':
    main()