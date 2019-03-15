import os
import sys
import config
from pathlib import Path
from post_man import SMTPPostMan, logger

target_dir = Path(config.target_dir)

if not target_dir.exists():
    os.makedirs(target_dir, exist_ok=True)

attached_target = target_dir / Path(config.attached_target_name)

# create file to send as attachment containing last 100 lines from debug.log
os.system(f"tail -n 100 {config.target_log_file} > {attached_target}")

try:
    message = sys.argv[1]
except IndexError:
    logger.error("Message argument is missing!")
    sys.exit(1)

mailer = SMTPPostMan(
    smtp_host=config.smtp_host,
    smtp_port=config.smtp_port,
    addr=config.addr,
    pwd=config.pwd
)

try:
    mailer.send_email(
        send_to=config.mail_receiver,
        subject=config.subject,
        text=message,
        attachments=[attached_target]
    )
except Exception:
    logger.critical("Failed to send email", exc_info=True)
else:
    os.system(f"rm {attached_target}")
