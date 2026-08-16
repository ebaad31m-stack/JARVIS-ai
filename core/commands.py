from core.app_launcher import (
    close_app,
    launch_app,
)

from core.browser_control import (
    open_website,
    search_google,
)

from core.screen_reader import (
    highlight_error_on_screen,
    highlight_text_on_screen,
    read_screen_text,
    summarize_screen_text,
)

from core.system_control import (
    shutdown_pc,
)

from core.system_info import (
    get_cpu,
    get_cpu_usage,
    get_gpu,
    get_gpu_stats,
    get_ram,
    get_ram_usage,
    get_storage,
    get_system_report,
    get_windows,
)

from core.vision_manager import (
    cancel_pending_click,
    click_pending_target,
    describe_screen,
    explain_screen_error,
    inspect_screen_question,
    locate_and_highlight,
    what_should_i_click,
)


def execute_command(
    command
):
    command = (
        command
        .lower()
        .strip()
    )

    # =========================================================
    # VISION CLICK CONFIRMATION
    # =========================================================

    if command in (
        "click it",
        "click that",
        "click the highlighted button",
        "click the highlighted target",
        "yes click it",
        "yes click that",
        "go ahead and click it",
        "go ahead click it",
        "press it",
        "press that",
    ):
        return click_pending_target()

    if command in (
        "cancel click",
        "cancel that",
        "don't click it",
        "do not click it",
        "never mind",
        "nevermind",
        "cancel the click",
    ):
        return cancel_pending_click()

    # =========================================================
    # TRUE AI SCREEN VISION
    # =========================================================

    if command in (
        "look at my screen",
        "analyze my screen",
        "analyse my screen",
        "describe my screen",
        "what do you see on my screen",
        "what can you see on my screen",
    ):
        return describe_screen()

    # =========================================================
    # EXPLAIN SCREEN ERROR
    # =========================================================

    if command in (
        "explain this error",
        "explain the error on my screen",
        "what is wrong with my screen",
        "what's wrong with my screen",
        "figure out this error",
        "help me with this error",
        "analyze this error",
        "analyse this error",
    ):
        return explain_screen_error()

    # =========================================================
    # WHAT SHOULD I CLICK
    # =========================================================

    if command in (
        "what should i click",
        "what do i click",
        "where should i click",
        "what should i press",
        "what do i press",
        "show me what to click",
        "highlight what i should click",
        "point to what i should click",
    ):
        return what_should_i_click()

    # =========================================================
    # VISION HIGHLIGHT SPECIFIC GUI ELEMENT
    # =========================================================

    vision_highlight_prefixes = (
        "show me where the ",
        "show me the ",
        "highlight the button ",
        "highlight the icon ",
        "highlight the menu ",
        "highlight the setting ",
        "highlight button ",
        "highlight icon ",
        "point to the button ",
        "point to the icon ",
        "find the button ",
        "find the icon ",
        "locate the ",
        "visually highlight ",
    )

    for prefix in vision_highlight_prefixes:
        if command.startswith(
            prefix
        ):
            target = command[
                len(prefix):
            ].strip()

            if target:
                return locate_and_highlight(
                    target
                )

    # =========================================================
    # CUSTOM VISION QUESTION
    # =========================================================

    vision_prefixes = (
        "look at my screen and ",
        "look at the screen and ",
        "analyze my screen and ",
        "analyse my screen and ",
        "look at this screen and ",
    )

    for prefix in vision_prefixes:
        if command.startswith(
            prefix
        ):
            question = command[
                len(prefix):
            ].strip()

            if question:
                return inspect_screen_question(
                    question
                )

    # =========================================================
    # FAST OCR SCREEN READING
    # =========================================================

    if command in (
        "read my screen",
        "read the screen",
        "what is on my screen",
        "what's on my screen",
        "tell me what is on my screen",
        "tell me what's on my screen",
    ):
        text = read_screen_text()

        if not text:
            return (
                "I couldn't detect any readable "
                "text on your screen."
            )

        spoken_text = (
            summarize_screen_text(
                text
            )
        )

        return (
            "I can see the following text. "
            + spoken_text
        )

    # =========================================================
    # OCR HIGHLIGHT ERROR
    # =========================================================

    if command in (
        "highlight the error",
        "highlight error",
        "show me the error",
        "point to the error",
        "where is the error",
        "find the error",
    ):
        found = (
            highlight_error_on_screen()
        )

        if found:
            return (
                "I found a possible error "
                "and highlighted it."
            )

        return (
            "I couldn't find an obvious "
            "error on the screen."
        )

    # =========================================================
    # OCR HIGHLIGHT SPECIFIC TEXT
    # =========================================================

    highlight_prefixes = (
        "highlight text ",
        "find text ",
        "point to text ",
    )

    for prefix in highlight_prefixes:
        if command.startswith(
            prefix
        ):
            target = command[
                len(prefix):
            ].strip()

            if not target:
                continue

            found = highlight_text_on_screen(
                target,
                label=(
                    f"Found: {target}"
                ),
            )

            if found:
                return (
                    f"I found {target} "
                    "and highlighted it."
                )

            return (
                f"I couldn't find {target} "
                "on the screen."
            )

    # =========================================================
    # CLOSE APPS
    # =========================================================

    if command.startswith(
        "close "
    ):
        app_name = command.replace(
            "close ",
            "",
            1,
        ).strip()

        result = close_app(
            app_name
        )

        if result is True:
            return (
                f"Closing {app_name}."
            )

        if result is False:
            return (
                f"I couldn't close {app_name}."
            )

    if command.startswith(
        "quit "
    ):
        app_name = command.replace(
            "quit ",
            "",
            1,
        ).strip()

        result = close_app(
            app_name
        )

        if result is True:
            return (
                f"Closing {app_name}."
            )

        if result is False:
            return (
                f"I couldn't close {app_name}."
            )

    # =========================================================
    # BROWSER CONTROL
    # =========================================================

    if command.startswith(
        "search google for "
    ):
        query = command.replace(
            "search google for ",
            "",
            1,
        ).strip()

        if search_google(
            query
        ):
            return (
                f"Searching Google for {query}."
            )

    if command.startswith(
        "search for "
    ):
        query = command.replace(
            "search for ",
            "",
            1,
        ).strip()

        if search_google(
            query
        ):
            return (
                f"Searching Google for {query}."
            )

    if command.startswith(
        "open website "
    ):
        website = command.replace(
            "open website ",
            "",
            1,
        ).strip()

        if open_website(
            website
        ):
            return (
                f"Opening {website}."
            )

    if (
        command.startswith(
            "open "
        )
        and "." in command
    ):
        website = command.replace(
            "open ",
            "",
            1,
        ).strip()

        if open_website(
            website
        ):
            return (
                f"Opening {website}."
            )

    # =========================================================
    # APP LAUNCHER
    # =========================================================

    if command.startswith(
        "open "
    ):
        app_name = command.replace(
            "open ",
            "",
            1,
        ).strip()

        result = launch_app(
            app_name
        )

        if result is True:
            return (
                f"Opening {app_name}."
            )

        if result is False:
            return (
                f"I couldn't open {app_name}."
            )

    if command.startswith(
        "launch "
    ):
        app_name = command.replace(
            "launch ",
            "",
            1,
        ).strip()

        result = launch_app(
            app_name
        )

        if result is True:
            return (
                f"Opening {app_name}."
            )

        if result is False:
            return (
                f"I couldn't open {app_name}."
            )

    # =========================================================
    # SYSTEM INFORMATION
    # =========================================================

    if command == "what cpu do i have":
        return (
            f"You have: {get_cpu()}."
        )

    if command == "what ram do i have":
        return (
            f"You have {get_ram()} of RAM."
        )

    if command == "what windows version am i using":
        return (
            f"You are running {get_windows()}."
        )

    if command == "what gpu do i have":
        return (
            f"You have: {get_gpu()}."
        )

    if command == "how much storage do i have":
        return (
            f"You have {get_storage()}."
        )

    if command == "what is my cpu usage":
        return (
            f"Your CPU usage is "
            f"{get_cpu_usage()}."
        )

    if command == "how much ram am i using":
        return (
            f"You are using "
            f"{get_ram_usage()}."
        )

    if command == "what is my gpu status":
        return (
            f"GPU status: "
            f"{get_gpu_stats()}."
        )

    if command == "system report":
        return get_system_report()

    # =========================================================
    # UNKNOWN COMMAND
    # =========================================================

    return None