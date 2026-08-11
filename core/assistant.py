import time
import threading

from core.intent_router import process
from core.voice_output import speak, stop_voice
from core.voice_input import listen, listen_for_stop
from core.wake_word import wait_for_wake_word

from core.ui_state import (
    set_state,
    request_shutdown,
    request_text_input
)

from core.ai_mode import (
    set_ai_mode,
    get_ai_mode
)

from core.system_control import shutdown_pc
from core.gmail_manager import send_email
from core.contacts_manager import resolve_recipient


# =========================
# COMMAND LISTS
# =========================

SLEEP_COMMANDS = {
    "go to sleep",
    "sleep",
    "stop listening",
    "goodbye",
    "jarvis go",
    "jarvis sleep"
}


EXIT_COMMANDS = {
    "exit",
    "jarvis exit",
    "shut down jarvis",
    "shutdown jarvis"
}


NORMAL_MODE_COMMANDS = {
    "normal mode",
    "jarvis normal mode",
    "switch to normal mode",
    "use normal mode"
}


THINK_MODE_COMMANDS = {
    "think mode",
    "thinking mode",
    "jarvis think mode",
    "jarvis thinking mode",
    "switch to think mode",
    "switch to thinking mode",
    "use think mode"
}


PC_SHUTDOWN_COMMANDS = {
    "shut down my computer",
    "shutdown my computer",
    "shut down the computer",
    "shutdown the computer",
    "turn off my computer",
    "turn off the computer",
    "shut down my pc",
    "shutdown my pc",
    "turn off my pc"
}


SHUTDOWN_CONFIRM_COMMANDS = {
    "confirm shutdown",
    "confirm",
    "yes shut down",
    "yes shutdown",
    "yes"
}


SHUTDOWN_CANCEL_COMMANDS = {
    "cancel",
    "cancel shutdown",
    "no",
    "never mind",
    "nevermind"
}


EMAIL_START_COMMANDS = {
    "compose an email",
    "compose email",
    "send an email",
    "write an email",
    "write email"
}


EMAIL_CONFIRM_COMMANDS = {
    "confirm send",
    "send it",
    "send email",
    "send the email",
    "confirm"
}


EMAIL_EDIT_COMMANDS = {
    "edit email",
    "edit the email",
    "change email",
    "change the email"
}


EMAIL_CANCEL_COMMANDS = {
    "cancel",
    "cancel email",
    "cancel the email",
    "don't send",
    "do not send"
}


# =========================
# GLOBAL STATE
# =========================

IDLE_TIMEOUT = 120

speaking = False
stop_requested = False

shutdown_pending = False

email_mode = False
email_step = None

email_data = {
    "to": "",
    "subject": "",
    "body": ""
}


# =========================
# RESET EMAIL
# =========================

def reset_email():

    global email_mode
    global email_step
    global email_data

    email_mode = False
    email_step = None

    email_data = {
        "to": "",
        "subject": "",
        "body": ""
    }


# =========================
# SPEECH INTERRUPTION
# =========================

def interrupt_monitor():

    global speaking
    global stop_requested

    while speaking:

        try:

            if listen_for_stop():

                print(
                    "Interrupt detected!"
                )

                stop_requested = True

                stop_voice()

                speaking = False

                set_state(
                    "LISTENING"
                )

                break

        except Exception as error:

            print(
                "Interrupt error:",
                error
            )

            break


def speak_with_interrupt(text):

    global speaking
    global stop_requested

    stop_requested = False
    speaking = True

    set_state(
        "SPEAKING"
    )

    monitor = threading.Thread(
        target=interrupt_monitor,
        daemon=True
    )

    monitor.start()

    speech_thread = threading.Thread(
        target=speak,
        args=(text,),
        daemon=True
    )

    speech_thread.start()

    while speech_thread.is_alive():

        if stop_requested:

            stop_voice()

            break

        time.sleep(
            0.05
        )

    speaking = False

    if stop_requested:
        stop_voice()


# =========================
# THINKING INTERRUPTION
# =========================

def think_with_interrupt(command):

    global stop_requested

    stop_requested = False

    result = {
        "response": None,
        "finished": False
    }


    def ai_worker():

        try:

            result["response"] = process(
                command
            )

        except Exception as error:

            print(
                "AI processing error:",
                error
            )

            result["response"] = (
                "I encountered an error while "
                "processing that request."
            )

        finally:

            result["finished"] = True


    set_state(
        "THINKING"
    )

    ai_thread = threading.Thread(
        target=ai_worker,
        daemon=True
    )

    ai_thread.start()

    while not result["finished"]:

        try:

            if listen_for_stop():

                print(
                    "Thinking interrupted!"
                )

                stop_requested = True

                set_state(
                    "LISTENING"
                )

                return None

        except Exception as error:

            print(
                "Thinking interrupt error:",
                error
            )

        time.sleep(
            0.05
        )

    return result[
        "response"
    ]


# =========================
# EMAIL RECIPIENT POPUP
# =========================

def ask_for_recipient():

    set_state(
        "SPEAKING"
    )

    speak(
        "Enter the recipient, sir."
    )

    typed_recipient = request_text_input(
        "Compose Email",
        "Enter an email address or contact name:"
    )

    if not typed_recipient:
        return None

    recipient = resolve_recipient(
        typed_recipient
    )

    return recipient


# =========================
# MAIN ASSISTANT
# =========================

def start_assistant():

    global stop_requested
    global shutdown_pending

    global email_mode
    global email_step
    global email_data

    # =========================
    # STARTUP
    # =========================

    set_state(
        "SPEAKING"
    )

    speak(
        "JARVIS is online."
    )

    # =========================
    # WAKE LOOP
    # =========================

    while True:

        set_state(
            "IDLE"
        )

        print(
            "Waiting for wake word..."
        )

        wait_for_wake_word()

        set_state(
            "SPEAKING"
        )

        speak(
            "I'm listening."
        )

        set_state(
            "LISTENING"
        )

        last_activity = time.time()

        # =========================
        # ACTIVE LOOP
        # =========================

        while True:

            raw_command = listen()

            # =========================
            # IDLE TIMEOUT
            # =========================

            if not raw_command:

                if (
                    time.time()
                    - last_activity
                    > IDLE_TIMEOUT
                ):

                    reset_email()
                    shutdown_pending = False

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Going back to sleep."
                    )

                    set_state(
                        "IDLE"
                    )

                    break

                continue

            last_activity = time.time()

            raw_command = (
                raw_command.strip()
            )

            command = (
                raw_command
                .lower()
                .strip()
            )

            # =========================
            # EXIT JARVIS
            # =========================

            if command in EXIT_COMMANDS:

                reset_email()

                set_state(
                    "SPEAKING"
                )

                speak(
                    "JARVIS shutting down."
                )

                set_state(
                    "IDLE"
                )

                request_shutdown()

                return

            # =========================
            # PC SHUTDOWN CONFIRMATION
            # =========================

            if shutdown_pending:

                if (
                    command
                    in SHUTDOWN_CONFIRM_COMMANDS
                ):

                    shutdown_pending = False

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Shutting down, sir."
                    )

                    shutdown_pc()

                    return

                if (
                    command
                    in SHUTDOWN_CANCEL_COMMANDS
                ):

                    shutdown_pending = False

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Shutdown cancelled."
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

                set_state(
                    "SPEAKING"
                )

                speak(
                    "Please say confirm shutdown, "
                    "or cancel shutdown."
                )

                set_state(
                    "LISTENING"
                )

                continue

            # =========================
            # AI MODE SWITCHING
            # =========================

            # We don't switch modes in the middle
            # of composing an email.

            if not email_mode:

                if command in NORMAL_MODE_COMMANDS:

                    if get_ai_mode() == "normal":

                        set_state(
                            "SPEAKING"
                        )

                        speak(
                            "Normal mode is already active, sir."
                        )

                    else:

                        set_ai_mode(
                            "normal"
                        )

                        print(
                            "AI mode changed to NORMAL"
                        )

                        set_state(
                            "SPEAKING"
                        )

                        speak(
                            "Normal mode activated, sir."
                        )

                    set_state(
                        "LISTENING"
                    )

                    continue


                if command in THINK_MODE_COMMANDS:

                    if get_ai_mode() == "think":

                        set_state(
                            "SPEAKING"
                        )

                        speak(
                            "Think mode is already active, sir."
                        )

                    else:

                        set_ai_mode(
                            "think"
                        )

                        print(
                            "AI mode changed to THINK"
                        )

                        set_state(
                            "SPEAKING"
                        )

                        speak(
                            "Think mode activated, sir."
                        )

                    set_state(
                        "LISTENING"
                    )

                    continue

            # =========================
            # EMAIL MODE
            # =========================

            if email_mode:

                # -------------------------
                # CANCEL EMAIL
                # -------------------------

                if command in EMAIL_CANCEL_COMMANDS:

                    reset_email()

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Email cancelled, sir."
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

                # -------------------------
                # SUBJECT
                # -------------------------

                if email_step == "subject":

                    email_data[
                        "subject"
                    ] = raw_command

                    email_step = "body"

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "What would you like me to say?"
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

                # -------------------------
                # BODY
                # -------------------------

                if email_step == "body":

                    email_data[
                        "body"
                    ] = raw_command

                    email_step = "confirm"

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "The email is ready. "
                        "Say confirm send, "
                        "edit email, or cancel."
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

                # -------------------------
                # CONFIRM / EDIT
                # -------------------------

                if email_step == "confirm":

                    if (
                        command
                        in EMAIL_CONFIRM_COMMANDS
                    ):

                        set_state(
                            "THINKING"
                        )

                        success = send_email(
                            email_data["to"],
                            email_data["subject"],
                            email_data["body"]
                        )

                        if success:

                            set_state(
                                "SPEAKING"
                            )

                            speak(
                                "Email sent, sir."
                            )

                        else:

                            set_state(
                                "SPEAKING"
                            )

                            speak(
                                "I couldn't send "
                                "the email, sir."
                            )

                        reset_email()

                        set_state(
                            "LISTENING"
                        )

                        continue

                    if (
                        command
                        in EMAIL_EDIT_COMMANDS
                    ):

                        email_step = (
                            "edit_choice"
                        )

                        set_state(
                            "SPEAKING"
                        )

                        speak(
                            "Which part would you like "
                            "to edit? Recipient, "
                            "subject, or body?"
                        )

                        set_state(
                            "LISTENING"
                        )

                        continue

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Please say confirm send, "
                        "edit email, or cancel."
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

                # -------------------------
                # EDIT CHOICE
                # -------------------------

                if email_step == "edit_choice":

                    if command in {
                        "recipient",
                        "edit recipient",
                        "change recipient"
                    }:

                        recipient = (
                            ask_for_recipient()
                        )

                        if not recipient:

                            set_state(
                                "SPEAKING"
                            )

                            speak(
                                "Recipient edit cancelled."
                            )

                            email_step = (
                                "confirm"
                            )

                            set_state(
                                "LISTENING"
                            )

                            continue

                        email_data[
                            "to"
                        ] = recipient

                        print(
                            "Updated email recipient:",
                            recipient
                        )

                        email_step = (
                            "confirm"
                        )

                        set_state(
                            "SPEAKING"
                        )

                        speak(
                            "Recipient updated. "
                            "Say confirm send, "
                            "edit email, or cancel."
                        )

                        set_state(
                            "LISTENING"
                        )

                        continue


                    if command in {
                        "subject",
                        "edit subject",
                        "change subject"
                    }:

                        email_step = (
                            "edit_subject"
                        )

                        set_state(
                            "SPEAKING"
                        )

                        speak(
                            "What should the new "
                            "subject be, sir?"
                        )

                        set_state(
                            "LISTENING"
                        )

                        continue


                    if command in {
                        "body",
                        "message",
                        "edit body",
                        "change body",
                        "edit message",
                        "change message"
                    }:

                        email_step = (
                            "edit_body"
                        )

                        set_state(
                            "SPEAKING"
                        )

                        speak(
                            "What should the new "
                            "message say, sir?"
                        )

                        set_state(
                            "LISTENING"
                        )

                        continue

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Please say recipient, "
                        "subject, or body."
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

                # -------------------------
                # EDIT SUBJECT
                # -------------------------

                if email_step == "edit_subject":

                    email_data[
                        "subject"
                    ] = raw_command

                    email_step = (
                        "confirm"
                    )

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Subject updated. "
                        "Say confirm send, "
                        "edit email, or cancel."
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

                # -------------------------
                # EDIT BODY
                # -------------------------

                if email_step == "edit_body":

                    email_data[
                        "body"
                    ] = raw_command

                    email_step = (
                        "confirm"
                    )

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Message updated. "
                        "Say confirm send, "
                        "edit email, or cancel."
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

            # =========================
            # START EMAIL
            # =========================

            if command in EMAIL_START_COMMANDS:

                reset_email()

                recipient = ask_for_recipient()

                if not recipient:

                    set_state(
                        "SPEAKING"
                    )

                    speak(
                        "Email cancelled, sir."
                    )

                    set_state(
                        "LISTENING"
                    )

                    continue

                print(
                    "Email recipient:",
                    recipient
                )

                email_mode = True
                email_step = "subject"

                email_data = {
                    "to": recipient,
                    "subject": "",
                    "body": ""
                }

                set_state(
                    "SPEAKING"
                )

                speak(
                    "What should the subject be, sir?"
                )

                set_state(
                    "LISTENING"
                )

                continue

            # =========================
            # PC SHUTDOWN REQUEST
            # =========================

            if command in PC_SHUTDOWN_COMMANDS:

                shutdown_pending = True

                set_state(
                    "SPEAKING"
                )

                speak(
                    "Are you sure, sir? "
                    "Say confirm shutdown."
                )

                set_state(
                    "LISTENING"
                )

                continue

            # =========================
            # SLEEP
            # =========================

            if command in SLEEP_COMMANDS:

                reset_email()

                set_state(
                    "SPEAKING"
                )

                speak(
                    "Going back to sleep."
                )

                set_state(
                    "IDLE"
                )

                break

            # =========================
            # NORMAL COMMAND
            # =========================

            speak_with_interrupt(
                "One moment, sir."
            )

            if stop_requested:

                stop_requested = False

                set_state(
                    "LISTENING"
                )

                continue

            # =========================
            # PROCESS
            # =========================

            response = think_with_interrupt(
                command
            )

            if stop_requested:

                stop_requested = False

                set_state(
                    "LISTENING"
                )

                continue

            # =========================
            # SPEAK RESPONSE
            # =========================

            if response:

                speak_with_interrupt(
                    response
                )

            stop_requested = False

            set_state(
                "LISTENING"
            )