#SNDesktop – ServiceNow Desktop Notifications

SNDesktop is a lightweight Python-based installer and poller program that listens for notifications from your ServiceNow instance and displays them as Windows desktop notifications.
Setup

    Install Update Set
    Import the Desktop Notifications.xml update set into your ServiceNow instance.

        Navigate to System Update Sets > Retrieved Update Sets

        Upload, Preview, and Commit the update set.

    Install Desktop Notifier

        Run installer.exe.

        Register your machine using Basic Auth.
        Note: SSO is not yet supported (PRs or ideas welcome!).

    Run Poller

        Launch poller.exe.

        Verify that your machine appears in the u_desktop_notifications_registered_machines table in your instance.

Usage

    Trigger a notification in ServiceNow (e.g., a sys_email record with type = send).

    Within 10 seconds, the desktop notifier should display the message.

Notes & Disclaimer

    This project is provided as-is, with no warranty implied.

    Functionality may break or change over time.

    Feel free to fork or open a PR to contribute improvements (especially around SSO support).